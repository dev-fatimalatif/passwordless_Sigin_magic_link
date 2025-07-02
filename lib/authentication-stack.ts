import * as cdk from 'aws-cdk-lib';
import { Duration } from 'aws-cdk-lib/core'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import { RetentionDays } from 'aws-cdk-lib/aws-logs'
import { Construct } from 'constructs';
import { CfnOutput } from "aws-cdk-lib";
import * as cg from 'aws-cdk-lib/aws-cognito';
import { aws_iam as iam } from "aws-cdk-lib";
import {createLambdas}  from './helpers/authentication-lambdas'
import { config } from './config/appConfig';
import {postConfirmation} from'./helpers/postConfirmation-lambda'
import { getResourceId } from "./helpers/config-utils";

// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class cognitoStack extends cdk.Stack {
  public readonly userPool: cg.UserPool;
  constructor(scope: Construct, id: string, 
    props?: cdk.StackProps) {
    super(scope, id, props);
    // Use the config object to access environment-specific values
    const { environment, awsRegion } = config;

    const lambdas = createLambdas(this); // Returns a map of Lambda functions

    // Create the Lambda function and automatically grant it permissions for the DynamoDB table
    const postConfirmationFunction = postConfirmation(this, 'postConfirmation');

    // The code that defines your stack goes here
    this.userPool = new cg.UserPool(this, 'usersPool', {
      userPoolName: `${config.stackName}-${config.app}-cognitoUserPool`,
      standardAttributes: { email: { required: true, mutable: true } },
      customAttributes: {
        authChallenge: new cg.StringAttribute({ mutable: true }),
      },
      passwordPolicy: {
        minLength: 8,
        requireDigits: true,
        requireUppercase: true,
        requireSymbols: true,
      },
      accountRecovery: cg.AccountRecovery.NONE,
      selfSignUpEnabled: true,
  
      signInAliases: { email: true },
      lambdaTriggers: {
        preSignUp:lambdas['preSignUp'],
        createAuthChallenge: lambdas['createAuthChallenge'],
        defineAuthChallenge: lambdas['defineAuthChallenge'],
        verifyAuthChallengeResponse: lambdas['verifyAuthChallenge'],
        postConfirmation: postConfirmationFunction,

      },
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    })

    // Add Google Identity Provider (check if region supports Google IdP)
    const googleIdp = new cg.UserPoolIdentityProviderGoogle(this, 'GoogleIdP', {
      clientId: process.env.GOOGLE_CLIENT_ID || '',  // Securely set via environment variable
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '', // Securely set via environment variable
      userPool: this.userPool,
      scopes: ['profile', 'email', 'openid'], // Authorized scopes
      attributeMapping: {
        email: cg.ProviderAttribute.GOOGLE_EMAIL, // Map Google email to user pool email
      },
    });

    // Create Web Client for User Pool
  
    const webClient = this.userPool.addClient('webAppClient', {
      userPoolClientName: `${config.stackName}-${config.app}-userPoolClient`,
      generateSecret: false,
      supportedIdentityProviders: [
        cg.UserPoolClientIdentityProvider.GOOGLE,
      ],
      
      authFlows: {
        userPassword: true,  // ALLOW_USER_PASSWORD_AUTH
        custom: true, 
        userSrp: true,

      },
     // Logout URL
      oAuth: {
        flows: {
          authorizationCodeGrant: true, // Code flow
          implicitCodeGrant: true, // Implicit flow
        },
        scopes: [
          cg.OAuthScope.EMAIL, // email scope
          cg.OAuthScope.OPENID, // openid scope
          cg.OAuthScope.PROFILE, // profile scope
        ],
      },
     
    });

    const identityPool = new cg.CfnIdentityPool(this, "IdentityPool", {
      identityPoolName: `${config.stackName}-${config.app}-IdentityPool`, // * Identity Pool Name
      allowUnauthenticatedIdentities: false,
      cognitoIdentityProviders: [
        {
          clientId: webClient.userPoolClientId,
          // providerName: userPool.userPoolProviderName,
          providerName: this.userPool.userPoolProviderName
        },
      ],
    });

    const authenticatedRole = new iam.Role(
      this,
      "CognitoDefaultAuthenticatedRole",
      {
        assumedBy: new iam.FederatedPrincipal(
          "cognito-identity.amazonaws.com",
          {
            StringEquals: {
              "cognito-identity.amazonaws.com:aud": identityPool.ref,
            },
            "ForAnyValue:StringLike": {
              "cognito-identity.amazonaws.com:amr": "authenticated",
            },
          },
          "sts:AssumeRoleWithWebIdentity"
        ),
      }
    );

    const unauthenticatedRole = new iam.Role(
      this,
      "CognitoDefaultUnauthenticatedRole",
      {
        assumedBy: new iam.FederatedPrincipal(
          "cognito-identity.amazonaws.com",
          {
            StringEquals: {
              "cognito-identity.amazonaws.com:aud": identityPool.ref,
            },
            "ForAnyValue:StringLike": {
              "cognito-identity.amazonaws.com:amr": "unauthenticated",
            },
          },
          "sts:AssumeRoleWithWebIdentity"
        ),
      }
    );

    // Attach the S3 access policy to the authenticated role
    authenticatedRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["s3:PutObject", "s3:GetObject"],
        resources: [
          `arn:aws:s3:::${config.stackName}-${config.app}-mediastorage`,
          `arn:aws:s3:::${config.stackName}-${config.app}-mediastorage/*`,
        ],
      })
    );

    new cg.CfnIdentityPoolRoleAttachment(
      this,
      "IdentityPoolRoleAttachment",
      {
        identityPoolId: identityPool.ref,
        roles: {
          authenticated: authenticatedRole.roleArn,
          unauthenticated: unauthenticatedRole.roleArn,
        },
      }
    );
    // Make sure the user pool client is created after the IDP
    webClient.node.addDependency(googleIdp);
    new CfnOutput(this, "userPoolArn-Arn", {
      value: this.userPool.userPoolArn,
      exportName: 'awsUserPoolArn',
    });

    new cdk.CfnOutput(this, 'userPoolId', {
      value: this.userPool.userPoolId,
      exportName: "awsUserPoolId"
    })

    new cdk.CfnOutput(this, 'clientId', {
      value: webClient.userPoolClientId,
      exportName: "awsClientId"
    })
  }
}
    
        



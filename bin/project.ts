import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { cognitoStack } from "../lib/authentication-stack";
import { config } from '../lib/config/appConfig';


class MyCDKApp extends cdk.App {
  constructor() {
    super();
    const cognito = new cognitoStack(this, `${config.stackName}-cognitoStack`, {
      env: config.aws_env, // Pass the environment configuration to the stack
    });
  }
}

new MyCDKApp();

import * as path from 'path';
import { Construct } from 'constructs';

import { Stack, StackProps } from 'aws-cdk-lib';
import { Bucket, EventType } from 'aws-cdk-lib/aws-s3';
import { Runtime, Code, Function } from 'aws-cdk-lib/aws-lambda';
import { S3EventSource } from 'aws-cdk-lib/aws-lambda-event-sources';
import { AnyPrincipal, PolicyStatement } from 'aws-cdk-lib/aws-iam';

export class WordsearchPuzzleStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const bucket = new Bucket(this, 'WordsearchPuzzleBucket', {
      bucketName: 'wordsearch-puzzle-01234'  
    });

    bucket.grantPublicAccess();
    bucket.addToResourcePolicy(
      new PolicyStatement({
        principals: [new AnyPrincipal()],
        actions: ['s3:GetObject'],
        resources: [bucket.arnForObjects('puzzle/*')],
      })
    )

    // Trigger: S3 Upload, matching the words/<filename>.json
    // Lambda: Generate puzzle, upload to generated/<filename>.md
    const generatorLambda = new Function(this, 'GeneratorFunction', {
      description: 'Generate the puzzle and upload it to S3',
      runtime: Runtime.PYTHON_3_12, 
      handler: 'index.handler',
      code: Code.fromAsset(path.join(__dirname, '../lambda/generator'), {
        bundling: {
          image: Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }),
      environment: {
        OUTPUT_DIR: 'generated/',
      }
    });
    bucket.grantReadWrite(generatorLambda);
    generatorLambda.addEventSource(new S3EventSource(bucket, {
      events: [EventType.OBJECT_CREATED],
      filters: [{
        prefix: 'words/',
        suffix: '.json',
      }]
    }))

    // Trigger: S3 Upload, matching generated/<filename>.md
    // Lambda: Convert to PDF, upload to puzzle/<filename>.pdf
    const converterLambda = new Function(this, 'ConverterFunction', {
      description: 'Convert the puzzle to PDF and upload it to S3',
      runtime: Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: Code.fromAsset(path.join(__dirname, '../lambda/convertor'), {
        bundling: {
          image: Runtime.PYTHON_3_11.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }), 
      environment: {
        OUTPUT_DIR: 'puzzle/',
      }   
    });
    bucket.grantReadWrite(converterLambda);
    converterLambda.addEventSource(new S3EventSource(bucket, {
      events: [EventType.OBJECT_CREATED],
      filters: [{
        prefix: 'generated/',
        suffix: '.md',
      }]
    }))
  }
}

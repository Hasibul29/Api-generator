from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    file_exists = None
    api = None

    if request.method == 'POST':
        lambda_file = request.files['lambda_file']
        somethingId = "{somethingId}"
        
       
        if os.path.exists(lambda_file.filename):
            print("File already exists")
        else:
            with open(lambda_file.filename, 'w') as f:
                f.write(lambda_file.read().decode('utf-8'))
        
        # print(api_name) # working
        # print(lambda_file) # working

        function_name = lambda_file.filename.split(".", 1)[0]

        # print(function_name)

        os.system(f'zip {function_name}.zip {lambda_file.filename}')
        os.system(f'awslocal lambda create-function \
                --function-name {function_name} \
                --runtime python3.9 \
                --zip-file fileb://{function_name}.zip \
                --handler {function_name}.lambda_handler \
                --role arn:aws:iam::000000000000:role/lambda-role')

        api_key = os.popen(f'awslocal apigateway create-rest-api --name {function_name}').read().split()[3]

        # print("api_key  : "+api_key)

        parent_key = os.popen(f'awslocal apigateway get-resources --rest-api-id {api_key}').read().split()[1]

        # print("parent_key  : "+parent_key)

        resource_key = os.popen(f'awslocal apigateway create-resource \
                                --rest-api-id {api_key} --parent-id {parent_key}\
                                --path-part "{somethingId}"').read().split()[0]

        # print("resource_key  : "+ resource_key)

        os.system(f'awslocal apigateway put-method --rest-api-id {api_key} \
                    --resource-id {resource_key} --http-method GET \
                    --request-parameters "method.request.path.somethingId=true" \
                    --authorization-type "NONE"')

        os.system(f'awslocal apigateway put-integration \
                  --rest-api-id {api_key} \
                  --resource-id {resource_key} \
                  --http-method GET \
                  --type AWS_PROXY \
                  --integration-http-method POST \
                  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:{function_name}/invocations \
                  --passthrough-behavior WHEN_NO_MATCH')

        os.system(f'awslocal apigateway create-deployment \
                    --rest-api-id {api_key} \
                    --stage-name test')

        api = f'curl -X GET http://localhost:4566/restapis/{api_key}/test/_user_request_/test'

        # print(api) # works

    return render_template('index.html', file_exists=file_exists,api_exists=api)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

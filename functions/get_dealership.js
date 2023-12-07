function main(params) {
    secret = {
    "COUCH_URL": "https://d0c6fba4-de9e-4d5e-9ebb-c481b50fc836-bluemix.cloudantnosqldb.appdomain.cloud",
    "IAM_API_KEY": "gZR6u2C6-5oPNpg6TL9k1-BHGmefkotAlP_65ZJI0BkF",
    "COUCH_USERNAME": "d0c6fba4-de9e-4d5e-9ebb-c481b50fc836-bluemix"
    };

    return new Promise(function (resolve, reject) {
        const Cloudant = require('@cloudant/cloudant');
        const cloudant = Cloudant({
            url: secret.COUCH_URL,
            plugins: {iamauth: {iamApiKey:secret.IAM_API_KEY}}
        });
        const dealershipDb = cloudant.use('dealerships');

        if (params.dealerId) {
            // return dealership of specified dealership ID (if specified)
            dealershipDb.find({"selector": {"id": parseInt(params.dealerId)}},
                function (err, result) {
                        if (err) {
                            console.log(err)
                            reject(err);
                        }
                        let code=200;
                            if (result.docs.length==0) {
                                code= 404;
                            }
                        resolve({
                            statusCode: code,
                            headers: { 'Content-Type': 'application/json' },
                            body: result
                        });
                    });
        } else if (params.state) {
            // return dealerships for the specified state (if specified)
            dealershipDb.find({"selector": {"state": {"$eq": params.state}}},
                function (err, result) {
                        if (err) {
                            console.log(err)
                            reject(err);
                        }
                        let code=200;
                            if (result.docs.length==0) {
                                code= 404;
                            }
                        resolve({
                            statusCode: code,
                            headers: {'Content-Type': 'application/json'},
                            body: result
                        });
                    });
        } else {
            // return all documents if no parameters are specified
            dealershipDb.list(
                { include_docs: true },
                function (err, result) {
                    if (err) {
                        console.log(err)
                        reject(err);
                    }
                    resolve({
                        statusCode: 200,
                        headers: { 'Content-Type': 'application/json' },
                        body: result
                    });
                }
            );
        }
    });
}


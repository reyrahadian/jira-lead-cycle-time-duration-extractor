#!/usr/bin/env node
const AWS = require("aws-sdk");
const fs = require("fs");
const path = require("path");

const uploadToS3 = async (filePath, bucketName) => {
  const s3 = new AWS.S3();
  const fileContent = fs.readFileSync(filePath);
  const fileName = path.basename(filePath);

  const params = {
    Bucket: bucketName,
    Key: fileName,
    Body: fileContent
  };

  try {
    await s3.upload(params).promise();
    console.log(`Successfully uploaded ${fileName} to ${bucketName}`);
  } catch (err) {
    console.error("Error uploading to S3:", err);
    process.exit(1);
  }
};

if (process.argv.length !== 4) {
  console.error("Usage: node upload.js <filePath> <bucketName>");
  process.exit(1);
}

uploadToS3(process.argv[2], process.argv[3]);
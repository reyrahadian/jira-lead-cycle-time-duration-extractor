import { get } from 'request';
import { readFileSync, existsSync } from 'fs';
import { Auth } from '../types';

const configureGetOptions = (url: string, auth: Auth): any => {
  const options = {
    url,
    json: true,
    insecureHTTPParser: true,
  };
  // Handle OAuth (assumes OAuth handshake has been completed beforehand)
  if (auth.oauth && auth.oauth.private_key && auth.oauth.token) {
    const oauth = auth.oauth;
    Object.assign(options, { oauth });
  } else if (auth.username && auth.password) {
    // Handle Basic Auth
    const headers = {
      'Authorization': `Basic ${Buffer.from(auth.username + ':' + auth.password).toString('base64')}`, // server
      //'Authorization': `Bearer ${auth.password}`, // cloud
    };
    Object.assign(options, { headers });
  }
  // Handle Custom Self signed Cert
  /*
  if (existsSync('ca.cert.pem')) {
    const ca = readFileSync('ca.cert.pem');
    const agentOptions = { ca };
    Object.assign(options, { agentOptions });
  }
  */
  return options;
};

const getAsync = async (options:any): Promise<any>  => {
  return new Promise((accept, reject) => {
    get(options, (error:any, response:any, body:any) => {
      if (error) {
        console.log(`Error fetching json from ${options.url}`);
        reject(new Error(error));
      } else {
        if (typeof body === 'string') {
          if (body.includes('<title>Unauthorized (401)</title>')) {
            reject(new Error('Unauthorized'));
          }
        }
        accept(body);
      }
    });
  });
};

const getJson = async (url:any, auth:any) => {
  const options = configureGetOptions(url, auth);
  return getAsync(options);
};

export {
  getJson,
};
  export interface QueryBuilderOptions {
    apiRootUrl: string;
    nextPageToken: string;
    batchSize: number;
    jql: string;
  };

  const buildApiUrl = (rootUrl:string) => {
    rootUrl = rootUrl.substr(rootUrl.length - 1) === "/" ? rootUrl.substring(0, rootUrl.length - 1) : rootUrl;
    return `${rootUrl}/rest/api/3`;
  }

  const buildJiraSearchQueryUrl = ({ apiRootUrl, nextPageToken, batchSize, jql}: QueryBuilderOptions): string => {
    const query = `${buildApiUrl(apiRootUrl)}/search/jql?jql=${encodeURIComponent(jql)}&nextPageToken=${nextPageToken}&maxResults=${batchSize}&expand=changelog&fields=*all`;
    return query;
  };

  export {
    buildJiraSearchQueryUrl,
  };
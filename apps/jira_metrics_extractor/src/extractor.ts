import { populateStages } from './components/staging-parser';
import { getAttributes } from './components/fields-parser';
import { JiraWorkItem } from './components/jira-work-item';
import { getJson } from './components/jira-adapter';
import {
  JiraExtractorConfig,
  JiraApiIssue,
  JiraApiIssueQueryResponse,
  Auth,
  DurationIntervals,
} from './types';
import { buildJiraSearchQueryUrl } from './components/query-builder';

class JiraExtractor {
  config: JiraExtractorConfig;

  constructor(config: JiraExtractorConfig) {
    this.config = config;
  }

  async validate(): Promise<boolean> {
    const apiRootUrl = this.config.connection.url;
    if (!apiRootUrl) {
      throw new Error('URL for extraction not set.');
    }
    const jql = this.getJQL();
    const queryUrl: string = this.getJiraIssuesQueryUrl(jql);
    const testResponse: JiraApiIssueQueryResponse = await getJson(queryUrl, this.config.connection.auth);
    if (testResponse.errorMessages) {
      throw new Error(testResponse.errorMessages.join('\n'));
    }

    if (testResponse.issues.length === 0 && testResponse.isLast === true) {
      throw new Error(`No JIRA Issues found with the generated JQL:\n${jql}\nPlease modify your configuration.`);
    }
``
    if (!testResponse.issues) {
      throw new Error(`Error calling JIRA API at the following url:\n${queryUrl}\n using JQL: ${jql}`);
    }
    return true;
  }

  async extractAll(debug: boolean = false): Promise<JiraWorkItem[]> {
    await this.validate();

    const config: JiraExtractorConfig = this.config;
    const auth: Auth = config.connection.auth;
    const batchSize: number = config.batchSize || 10;
    const jql: string = this.getJQL();

    if (debug) {
      console.log(`Using the following JQL for extracting:\n${jql}\n`);
    }

    const metadataQueryUrl: string = this.getJiraIssuesQueryUrl(jql, '', 1);
    const metadata: JiraApiIssueQueryResponse = await getJson(metadataQueryUrl, auth);
    const totalJiraCount: number = metadata.issues? metadata.issues.length : 0;
    const hasIssuesResult = totalJiraCount > 0 || metadata.isLast === false;
    if (!hasIssuesResult) {
      throw new Error(`No stories found under search conditions using the following JQL:
        ${jql}
        Please check your configuration.`);
    }

    let jiraWorkItemsAccumulator: JiraWorkItem[] = [];
    let nextPageToken: string = '';
    do {
      const apiResponse: JiraApiIssueQueryResponse = await this.getIssuesFromJira(jql, nextPageToken, batchSize);
      if (apiResponse.issues){
        if(nextPageToken === ''){
          console.debug("First sample: " + JSON.stringify(apiResponse.issues[0].fields));
        }

        const workItemBatch = apiResponse.issues.map(this.convertIssueToWorkItem);
        jiraWorkItemsAccumulator.push(...workItemBatch);

        console.debug(`Extracted ${workItemBatch.length} issues of page token: ${nextPageToken}`);
      }

      nextPageToken = apiResponse.nextPageToken;
    } while(nextPageToken && nextPageToken !== '');

    return jiraWorkItemsAccumulator;
  };

  private getStageNames(workItems: JiraWorkItem[]):string[]{
    let uniqueNames:string[] = null;

    workItems.forEach(issue => {
      const stageNames:string[] = issue.stages.size > 0 ? Array.from(issue.stages.keys()) : [];
      uniqueNames = Array.from(new Set(uniqueNames === undefined || uniqueNames == null ? stageNames: uniqueNames.concat(stageNames)));
    });

    return uniqueNames;
  }

  private getHeaderStageNames(stageNames:string[]):string[]{
    return stageNames.map((a) => `Stage ${a} days`);
  }

  private getHeaderStageStartDateNames(stageNames:string[]):string[]{
    return stageNames.map((a) => `Stage ${a} start`);
  }

  private getHeaderStageRecurrenceNames(stageNames:string[]):string[]{
    return stageNames.map((a) => `Stage ${a} recurrence`);
  }


  toCSV(workItems: JiraWorkItem[]) {
    console.log(" Extracting to csv ..")
    const SEP:string = ',';

    let attributes = this.config.attributes || {};
    let stageNames:string[] = this.getStageNames(workItems);
    let stageHeaderStageNames:string[] = this.getHeaderStageNames(stageNames);
    let stageHeaderStageStartNames:string[] = this.getHeaderStageStartDateNames(stageNames);
    let stageRecurrenceNames:string[] = this.getHeaderStageRecurrenceNames(stageNames);



    let headerArr:string[] = ["ID","Link","Name","Type"];
    headerArr = headerArr.concat(stageHeaderStageNames, stageHeaderStageStartNames, stageRecurrenceNames, Object.keys(attributes));
    headerArr = headerArr.map((a) => JiraWorkItem.cleanString(a));
    const header = headerArr.join(SEP);
    const body = workItems.map(item => item.toCSV(this.config, stageNames).join(SEP)).reduce((res, cur) => `${res + cur}\n`, '');
    const csv: string = `${header}\n${body}`;
    return csv;
  };

  private async getIssuesFromJira(jql:string, nextPageToken:string, batchSize:number): Promise<JiraApiIssueQueryResponse> {
    const queryUrl = this.getJiraIssuesQueryUrl(jql, nextPageToken, batchSize);
    const auth = this.config.connection.auth;
    const json: JiraApiIssueQueryResponse = await getJson(queryUrl, auth);

    if (!json.issues) {
      console.error("Issue sequence not parsed due to a timeout", JSON.stringify(json), jql, "nextPageToken: "+nextPageToken, "batchSize: "+batchSize);
      //throw new Error('Could not retrieve issues from object');
      return null;
    }

    return json;
  }

  private getJiraIssuesQueryUrl(jql: string, nextPageToken: string = '', batchSize: number = 1): string {
    const apiRootUrl = this.config.connection.url;
    const queryUrl: string = buildJiraSearchQueryUrl(
      {
        apiRootUrl,
        jql,
        nextPageToken: nextPageToken,
        batchSize: batchSize,
      });
    return queryUrl;
  }

  private getJQL(): string {
    return this.config.customJql;
  }

  private convertIssueToWorkItem = (issue: JiraApiIssue): JiraWorkItem => {
    const attributes = this.config.attributes;
    const key: string = issue.key;
    const name: string = issue.fields['summary'];
    const stagingDates: Map<string, DurationIntervals> = populateStages(issue);
    const type: string = issue.fields.issuetype.name ? issue.fields.issuetype.name : '';

    let attributesKeyVal = {};
    if (attributes) {
      const requestedAttributeSystemNames: string[] = Object.keys(attributes).map(key => attributes[key]);
      attributesKeyVal = getAttributes(issue.fields, requestedAttributeSystemNames);
    }

    return new JiraWorkItem(key, stagingDates, name, type, attributesKeyVal);
  };
};

export {
  JiraExtractor,
};

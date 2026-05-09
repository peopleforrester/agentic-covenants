-- ABOUTME: CloudWatch Logs Insights query listing every distinct AWS principal whose role name matches an agent naming convention.
-- ABOUTME: Run against the CloudTrail log group. Feed output into the operator-declared cross-reference job.

fields @timestamp,
       userIdentity.sessionContext.sessionIssuer.arn as role_arn,
       userIdentity.sessionContext.sessionIssuer.userName as role_name,
       sourceIPAddress,
       eventSource
| filter ispresent(userIdentity.sessionContext.sessionIssuer.userName)
| filter (
    userIdentity.sessionContext.sessionIssuer.userName like /^claude-/
    or userIdentity.sessionContext.sessionIssuer.userName like /-agent$/
    or userIdentity.sessionContext.sessionIssuer.userName like /-bot$/
    or userIdentity.sessionContext.sessionIssuer.userName like /^agent-/
  )
| stats count(*) as call_count,
        earliest(@timestamp) as first_seen,
        latest(@timestamp) as last_seen,
        count_distinct(sourceIPAddress) as distinct_source_ips
  by role_name, role_arn
| sort last_seen desc
| limit 200

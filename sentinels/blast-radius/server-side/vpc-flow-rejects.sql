-- ABOUTME: CloudWatch Logs Insights query for VPC Flow REJECT records sourced from agent pod CIDRs.
-- ABOUTME: Run on the VPC Flow Logs log group; substitute agent_pod_cidrs for your environment's actual CIDRs.

fields @timestamp, srcAddr, dstAddr, dstPort, action, protocol
| filter srcAddr in [
    -- Substitute your agent namespaces' Pod CIDRs.
    "10.100.1.0/24",
    "10.100.2.0/24"
  ]
| filter action = "REJECT"
| stats count() as rejects by dstAddr, dstPort
| sort rejects desc
| limit 25

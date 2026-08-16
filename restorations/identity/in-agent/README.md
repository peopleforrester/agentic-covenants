# Restorations, Identity / In-agent

**Empty by design.** The agent is not part of its own recovery. Real rebuild lives in [`../client-side/`](../client-side/) (regenerate credential, restore ACLs) and [`../server-side/`](../server-side/) (recreate ServiceAccount, rotate keys, re-establish OIDC trust).

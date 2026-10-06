Act as a threat modeler using STRIDE. Here is the architecture:
- React SPA -> API Gateway -> Flask service -> Postgres
- Auth via JWT issued by an external IdP; uploads go to S3 via presigned URLs
- Admin panel on the same API under /admin

For each STRIDE category, list the top 2 realistic threats, the affected component,
a concrete attack scenario, and a mitigation. Finish with a table ranked by risk
(likelihood x impact) and 3 test cases I should run in staging.
Be concise: one sentence each for scenario and mitigation, under 450 words in total.

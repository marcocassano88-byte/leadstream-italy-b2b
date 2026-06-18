# leadstream-italy-b2b

Automated Data-as-a-Service (DaaS) pipeline that aggregates, cleans, and enriches high-value B2B tech leads in Italy. 

## 📊 Dataset Specifications
- **Target**: Software Houses, SaaS, Digital Agencies, and Tech Startups operating in Italy.
- **Update Frequency**: Daily (automated at 02:00 UTC).
- **Format**: Structured CSV ready for CRM injection (HubSpot, Salesforce) or outbound campaigns.

## 🚀 Automated Workflow
This repository runs 100% on autopilot via GitHub Actions. Every 24 hours, the system:
1. Scrapes open-data tech directories.
2. Deduplicates leads based on domain uniqueness.
3. Classifies sectors using deterministic keyword matching.
4. Appends new leads incrementally to `data/dataset_b2b_italy.csv`.

## 🛠️ Local Setup
1. Clone the repository:
```bash
   git clone [https://github.com/YOUR_USERNAME/leadstream-italy-b2b.git](https://github.com/YOUR_USERNAME/leadstream-italy-b2b.git)
   cd leadstream-italy-b2b

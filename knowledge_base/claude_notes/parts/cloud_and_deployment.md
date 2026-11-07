<!-- topics: dev_tools,networking,web_security -->
# Cloud Computing and Deploying a Project

## What the cloud is, in plain terms
Cloud computing means renting computing resources over the internet and paying for what you use, instead of buying and maintaining your own servers. The provider owns data centres in many regions, and you create virtual machines, storage, databases and networks with a few clicks or lines of configuration. The main benefits are speed (a server in minutes), elasticity (add or remove capacity as demand changes) and no hardware maintenance. The main risks are cost surprises, leaving things misconfigured, and depending on one provider.
The three service models describe how much the provider manages. Infrastructure as a Service (IaaS) gives you virtual machines, disks and networks, and you manage the operating system and everything above it. Platform as a Service (PaaS) gives you a place to run your code and you manage only the application and its data. Software as a Service (SaaS) is a finished application you just use, such as email or a document editor. The shared responsibility model says the provider secures the cloud itself, and you secure what you put in it: your data, accounts, configuration and access rules.

## Core building blocks
A virtual machine is a software-defined computer. A container packages an application with its dependencies and starts in seconds, and an orchestrator such as Kubernetes runs and restarts containers across many machines. Serverless functions run your code only when triggered and charge per execution, so you do not manage servers at all. Object storage holds files as objects in buckets, and it is cheap, durable and accessed over HTTP. Managed databases handle backups, patching and failover for you. A virtual private network inside the cloud (a VPC) is your private address space with subnets, route tables and security groups acting as virtual firewalls. A load balancer spreads traffic across several instances and checks their health, and DNS maps your domain name to the load balancer or server.
Regions and availability zones matter. A region is a geographic area, and an availability zone is an isolated data centre within it. Spreading instances across zones keeps the service alive when one zone fails, and choosing a region near your users reduces latency.

## Scaling and reliability
Vertical scaling makes one machine bigger. Horizontal scaling adds more machines, which usually scales further and survives failures, but it needs the application to be stateless, meaning requests do not depend on data kept in the memory or on the disk of one instance. Keep state in a database, a cache or object storage. Caches such as Redis reduce database load. Health checks remove broken instances from rotation. Design for failure: assume that any machine can disappear and that a request can be retried, which is why write operations should be idempotent where possible.

## Configuration and secrets: the twelve-factor ideas
Keep configuration out of the code, in environment variables. Treat backing services such as databases as attached resources defined by a URL. Make the build, release and run stages separate. Run the app as stateless processes, write logs to standard output, and let the platform collect them. Keep development and production as similar as possible. Never commit secrets such as API keys, tokens and passwords to Git: use environment variables, a .env file listed in .gitignore, or the secret store of the platform. If a secret was ever pushed to a repository, treat it as compromised and rotate it, because deleting the commit does not remove it from history or from copies.

## Containerising a Python web app
A typical Dockerfile for a FastAPI application looks like this.
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Copying requirements.txt and installing before copying the rest of the code lets Docker reuse the cached layer of installed packages when only your code changes, which makes rebuilds much faster. Binding to 0.0.0.0 is required so that the app is reachable from outside the container, since 127.0.0.1 inside a container is only the container itself. Add a .dockerignore file listing .git, .venv, __pycache__ and .env so they are not copied into the image.
Docker Compose runs several containers together. Services reach each other by service name on the internal network, so the app connects to the database at the host name db, not localhost.
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/appdb
    depends_on:
      - db
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: appdb
    volumes:
      - dbdata:/var/lib/postgresql/data
volumes:
  dbdata:
```
The named volume dbdata keeps the database files when the container is recreated. The passwords above are only for local practice, and real deployments should take them from a secret store. Start everything with docker compose up --build, and stop it with docker compose down.

## Continuous integration with GitHub Actions
A workflow is a YAML file in .github/workflows. It defines when it runs, on which kind of machine, and which steps to execute. This one runs the tests on every push and pull request.
```yaml
name: tests
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest
```
Make the main branch protected so that a pull request cannot be merged unless these checks pass. Store deployment credentials in the repository secrets and never in the workflow file. Extend the workflow with a linter, a dependency vulnerability scan and a build of the Docker image. Continuous delivery adds an automatic deployment step after the checks pass.

## Deploying: a practical path for a student project
For a first deployment, a PaaS or a container hosting service is the easiest because it handles servers, TLS certificates and restarts. A path that works: push the project to GitHub, connect the repository to the platform, set the environment variables in its dashboard, and let it build from the Dockerfile. If you rent a plain virtual machine instead, you must also manage updates, the firewall, a reverse proxy such as Nginx or Caddy for HTTPS, a process manager so the app restarts after a crash or reboot, and backups.
After deployment check these things: the app starts from a clean checkout using only the README instructions, the health endpoint answers, HTTPS works and HTTP redirects to it, secrets are not in the image or the repository, debug mode is off, and logs show errors. Add a simple health route such as /health that returns status ok, which monitoring tools and load balancers can poll.

## Domains, DNS and HTTPS
To use your own domain, register it, then create DNS records: an A record maps the name to an IPv4 address, an AAAA record to an IPv6 address, and a CNAME record points a name to another name, which is the usual way to connect a subdomain to a platform. DNS changes take time to spread because of caching, up to the TTL of the old record. Free automatic certificates from Let's Encrypt are issued after you prove control of the domain, and many platforms and servers such as Caddy renew them automatically. Certificates expire, and an expired certificate is a common cause of outages, so monitor expiry dates.

## Monitoring, logging and cost control
Monitoring answers whether the system is healthy, using metrics such as request rate, error rate, latency and resource use, and alerts that notify someone when thresholds are crossed. The useful starting set is the four golden signals: latency, traffic, errors and saturation. Logs explain why, and structured logs in JSON make searching easier. Tracing follows one request across services.
Costs can grow silently. Set a budget and billing alerts on day one, switch off resources you are not using, delete old snapshots and unattached disks, choose small instance sizes while testing, and remember that data leaving the provider (egress) is charged. Tag resources with the project name so you can see what each one costs. Free tiers have limits and expire, so read them before relying on them.

## Running an AI chatbot like this project in production
The model server and the web interface are separate concerns. Local models served by Ollama need a machine with enough memory, and a GPU makes them much faster, so a small cloud virtual machine without a GPU will answer slowly with a 7B model. Options are: run everything locally for the demo, rent a GPU machine only while needed, or call a hosted model API and keep only retrieval and the interface on your server. Keep the vector index and the SQLite knowledge base as files that are rebuilt by a script, so any machine can recreate them. Protect the interface with rate limiting, because every request costs compute, and never expose the Ollama port 11434 directly to the internet, since it has no authentication. Put it behind your application or a private network.

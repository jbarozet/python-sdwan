# Getting Started

## API Reference

Cisco Catalyst SD-WAN Manager API can be categorized in the following categories:

**Administrative and Settings APIs**:

- Includes user, group and tenant management, software maintenance, backup and restore, and container management.

**Monitoring and Troubleshooting**:

- Includes monitoring of devices, links, applications, systems, and so on
- Includes the alarm and event notification configuration, and alarm, event, and audit log queries

**UX 1.0 Configuration**:

- includes original device configuration, policy configuration
- device templates, feature templates.

**UX 2.0 Configuration**:

- Includes the new configuration framework
- with Configuration Groups, Policy Groups, and Topology Groups.

**Feature Profiles**:

include feature profiles associated with UX 2.0 configuration

- Feature Profiles: Solution SD-WAN, System
- Feature Profiles: Solution SD-WAN, Transport
- Feature Profiles: Solution SD-WAN, Service
- Feature Profiles: Solution SD-WAN, Others
- Feature Profiles: Solution SD-Routing
- Feature Profiles: Solutions Mobility and nfvirtual

**SD-WAN Services**:

- includes SD-WAN services
- like Cloud OnRamp for SaaS, MultiCloud

**Partner Integrations**:

- includes access to services from Webex, Secure Access and others
The following sections provide examples of the preceding categories. See Reference for an OpenAPI 3.0 Cisco Catalyst SD-WAN Manager API definition.

## Base URI

Every API request will begin with the following Base URI.

```example
https://<vmanage-server>:<port>/dataservice
```

## Authentication

See [Autentication](./02-Authentication.md)


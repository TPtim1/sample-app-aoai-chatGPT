# Infra files Description
contains the infrastructure deployment files to deploy in azure cloud
# main.bicep

Description: This is the main Bicep file that defines the infrastructure for deploying various Azure resources. It sets the target scope to the subscription level and includes parameters for environment configuration, resource names, and settings for services like OpenAI and Azure Search.

Key Components:

- Parameters for environment name, location, and various resource names.
- Resource group creation to organize resources.
- Modules for creating an App Service Plan, backend application, OpenAI resources, search services, and Cosmos DB.
- Role assignments for users and system identities.
- Outputs for various resource configurations.

# docprep.bicep

Description: This module is responsible for preparing documents using Azure services, specifically for form recognition.

Key Components:

- Parameters for resource group name, location, and form recognizer service settings.
- Resource group definition for organizing related resources.
- Module for creating a Form Recognizer service and assigning roles to users.
- Outputs for Form Recognizer service details.

# core/ai/cognitiveservices.bicep

Description: This module defines an Azure Cognitive Services account, which can be used for AI-related services like OpenAI.

Key Components:

- Parameters for account name, location, tags, and deployments.
- Resource definition for creating a Cognitive Services account with specified properties.
- Outputs the account's endpoint, ID, name, SKU name, and key.

# core/database/cosmos/sql/cosmos-sql-account.bicep

Description: This module creates an Azure Cosmos DB account specifically for SQL API.

Key Components:

- Parameters for account name, location, and tags.
- Module for creating a Cosmos DB account with specified properties.
- Outputs the endpoint, ID, and name of the Cosmos DB account.

# core/database/cosmos/sql/cosmos-sql-db.bicep

Description: This module creates a database within a Cosmos DB account for SQL API.

Key Components:

- Parameters for account name, database name, location, and container settings.
- Module for creating a Cosmos DB SQL database and its containers.
- Outputs the account ID, account name, database name, and endpoint.

# core/database/cosmos/sql/cosmos-sql-role-assign.bicep

Description: This Bicep module is responsible for creating a SQL role assignment under an Azure Cosmos DB account. It assigns a specified role to a principal (user, group, or service principal).

Key Components:

- Parameters for account name, role definition ID, and principal ID.
- Resource definition for creating a role assignment with specified properties.
- The role assignment links the principal to the role definition within the Cosmos DB account.

# core/database/cosmos/sql/cosmos-sql-role-def.bicep

Description: This Bicep module defines a custom SQL role for Azure Cosmos DB. It specifies the permissions associated with the role and the scopes where the role can be assigned.

Key Components:

- Parameters for account name.
- Resource definition for creating a SQL role definition with properties such as assignable scopes and permissions (data actions).
- Outputs the role definition ID, which can be used when assigning roles.


# core/database/cosmos/cosmos-account.bicep

Description: This module creates a general Azure Cosmos DB account.

Key Components:

- Parameters for account name, location, tags, and kind of account.
- Resource definition for creating the Cosmos DB account with specified properties.
- Outputs the account's endpoint and ID.

# core/host/appserviceplan.bicep

Description: This module creates an App Service Plan in Azure, which is required for hosting web applications.

Key Components:

- Parameters for the name, location, tags, and SKU of the App Service Plan.
- Resource definition for creating the App Service Plan with specified properties.
- Outputs the ID and name of the created App Service Plan.

# core/host/appservice.bicep

Description: This Bicep module creates an Azure App Service, which is used for hosting web applications and APIs.

Key Components:

- Parameters for application name, location, tags, runtime settings, and authentication.
- Resource definition for creating the App Service with specified properties, including site configuration and app settings.
- Outputs the App Service's identity principal ID, name, and URI.

# core/search/search-services.bicep

Description: This module creates an Azure Search service, which is used for indexing and querying data.

Key Components:

- Parameters for search service name, location, tags, SKU, and authentication options.
- Resource definition for creating the search service with specified properties.
- Outputs the search service's ID, endpoint, name, and admin key.

# core/security/role.bicep

Description: This Bicep module creates a role assignment in Azure, allowing specific users or service principals to have certain permissions on resources.

Key Components:

- Parameters for principal ID, principal type (e.g., user, group, service principal), and role definition ID.
- Resource definition for creating the role assignment with properties that link the principal to the specified role definition.
- This module is used to manage access control in Azure by assigning roles to users and services.

# core/storage/storage-account.bicep

Description: This Bicep module defines a storage account in Azure. It includes parameters for configuring the storage account, such as access tier, public access settings, and SKU.

Key Components:

- Parameters for storage account name, location, and properties like access tier and SKU.
- Resource definition for creating a storage account with optional blob services and containers.
- Outputs the storage account's name and primary endpoints.

# main.parameters.json

Description: This JSON file contains deployment parameters for the main Bicep file. It specifies values for various parameters used in the Bicep template.

Key Components:

- Parameters for environment name, location, principal ID, and resource names for OpenAI, Search Service, and Form Recognizer.
- Secure parameters for authentication credentials.

# abbreviations.json

Description: The abbreviations listed in the abbreviations.json file represent short forms used for various Azure resource types. These abbreviations are typically used to create resource names that are more concise while still conveying the type of resource being referenced.

# ERPNext Assistant

This Desk page answers questions using ERPNext DocType and report metadata from the checked-out ERPNext app. It does not read customer, employee, or other live site records. Questions are sent to Groq for intent detection, keyword extraction, and answer generation.

The assistant can also prepare a **User Creation Request** when asked to create a user. It extracts the name and email, plus any explicitly provided mobile number, phone, gender, birth date, language, or time zone. The request is linked in the chat and visible to its requester and System Managers. A System Manager with User create permission selects a desk-access role and approves it. Approval immediately creates an enabled System User with that role and does not send a welcome email; the reviewer is redirected to the new User profile.

The ERPNext repository does not include Frappe's core `User` DocType definition. These request fields are limited to identity and profile/contact fields referenced in ERPNext's User-related flows; access-critical fields such as roles, role profile, and User Type are not AI-assigned.

## Setup

Install the optional dependencies in the Bench environment:

```sh
bench pip install -e "apps/erpnext[rag]"
```

Set `groq_api_key` in the site configuration (or provide `GROQ_API_KEY` in the Bench process environment), then run `bench migrate` and `bench restart`. For example:

```sh
bench --site <site-name> set-config groq_api_key "<your-groq-api-key>"
```

After `bench migrate` and `bench restart`, the page is available at `/app/erpnext-assistant`. Rebuild the feature index after the new request DocType is installed if the catalog should include it.

The optional `groq_model` site setting selects the Groq model; by default the assistant uses `openai/gpt-oss-120b`.

## Rebuild the feature index

After changing ERPNext DocType or report metadata, run:

```sh
bench execute erpnext.utilities.page.erpnext_assistant.erpnext_assistant.build_index
bench restart
```

The index is built locally with `BAAI/bge-base-en-v1.5`; only the retrieved feature context and question are sent to Groq.

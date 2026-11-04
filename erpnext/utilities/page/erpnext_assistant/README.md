# ERPNext Assistant

This Desk page answers questions using ERPNext DocType and report metadata from the checked-out ERPNext app. It does not read customer, employee, or other live site records. Questions are sent to Groq for keyword extraction and answer generation.

## Setup

Install the optional dependencies in the Bench environment:

```sh
bench pip install -e "apps/erpnext[rag]"
```

Set `groq_api_key` in the site configuration (or provide `GROQ_API_KEY` in the Bench process environment), then run `bench migrate` and `bench restart`. For example:

```sh
bench --site <site-name> set-config groq_api_key "<your-groq-api-key>"
```

The page is available at `/app/erpnext-assistant`.

The optional `groq_model` site setting selects the Groq model; by default the assistant uses `openai/gpt-oss-120b`.

## Rebuild the feature index

After changing ERPNext DocType or report metadata, run:

```sh
bench execute erpnext.utilities.page.erpnext_assistant.erpnext_assistant.build_index
bench restart
```

The index is built locally with `BAAI/bge-base-en-v1.5`; only the retrieved feature context and question are sent to Groq.

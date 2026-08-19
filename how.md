# how

## Objective

`how` is a tool for generating command line commands with natural language.

## Toolchain

Language: Python
Supported LLMs: Gemini
Supported shells: bash
Dev Tools: uv
Libraries:
  - [google-genai](https://pypi.org/project/google-genai/): For interracting with the LLM.
  - [keyring](https://pypi.org/project/keyring/): For storing API keys.
  - [questionary](https://github.com/tmbo/questionary): For option selection.
  - [rich console status](https://rich.readthedocs.io/en/latest/console.html#status): For spinner animation.

## Assumptions

- Authentication credentials for one LLM provider can be used for all models from that provider.

## Examples

Typical usage:

```sh
$ how "View which process is eating the most memory?"

Thinking ...

Select command:
 * free -h
   watch -n 1 free -h
   top
   (None / Cancel)

$ free -h
```

Setting up an LLM provider:

```sh
$ how setup

Select LLM Provider:
 * Gemini
   OpenAI
   Mistral

Enter Gemini API Key:

Verifying API Key...
API Key Verified ✅

Select Model:
 * gemini-3.7-flash
   gemini-3.6-flash
   gemini-3.6-flash-lite

Setup Complete ✅
LLM Provider: Gemini
Default Model: gemini-3.7-flash

$
```

List all supported LLM providers:

```sh
$ how --list-supported-providers

Supported LLM Providers:
 - Gemini
 - OpenAI
 - Mistral

$
```

List all supported LLM providers:

```sh
$ how --list-configured-providers

Configured LLM Providers:
 - Gemini
 - OpenAI

Default LLM provider: Gemini

$
```

Set default LLM provider:

```sh
$ how --set-default-provider=Gemini

Success ✅
Default LLM Provider: Gemini

$
```

List supported models from a provider:

```sh
$ how --list-models=Gemini

Gemini Models:
 - gemini-3.7-flash
 - gemini-3.6-flash
 - gemini-3.6-flash-lite

Default Model: gemini-3.7-flash

$
```

Set default model for a provider:

```sh
$ how --set-default-model

Selct LLM Provider:
 * Gemini
   OpenAI

Select model:
 * gemini-3.7-flash
   gemini-3.6-flash
   gemini-3.6-flash-lite

Success ✅
Provider: Gemini
Default Model: gemini-3.7-flash

$
```

Clear credentials for a specific provider:

```sh
$ how --clear-credentials=Gemini

Gemini credentials cleared. Run 'how setup' to reconfigure.

$
```

## Implementation Notes

- Need to extract the users shell and OS and send that to the LLM.
- Need to provide instructions to the LLM on what it is supposed to do.
/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { createAnthropic, AnthropicProvider, AnthropicProviderSettings } from "@ai-sdk/anthropic";
import { BackendClient } from "@/backend/client.js";
import { getEnv } from "@/internals/env.js";
import { parseHeadersFromEnv, vercelFetcher } from "@/adapters/vercel/backend/utils.js";

export type AnthropicClientSettings = AnthropicProviderSettings;

export class AnthropicClient extends BackendClient<AnthropicClientSettings, AnthropicProvider> {
  protected create(): AnthropicProvider {
    const extraHeaders = parseHeadersFromEnv("ANTHROPIC_API_HEADERS");

    return createAnthropic({
      ...this.settings,
      baseURL: this.settings?.baseURL || getEnv("ANTHROPIC_API_BASE_URL"),
      apiKey: this.settings.apiKey || getEnv("ANTHROPIC_API_KEY"),
      headers: {
        ...extraHeaders,
        ...this.settings?.headers,
      },
      fetch: vercelFetcher(this.settings?.fetch),
    });
  }
}

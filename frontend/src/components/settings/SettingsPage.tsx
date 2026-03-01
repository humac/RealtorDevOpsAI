import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getLLMSettings, updateLLMSettings } from '../../services/api';
import type { LLMProvider, LLMProviderConfig, LLMSettings } from '../../types';

const PROVIDER_ICONS: Record<LLMProvider, string> = {
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  google: 'Google',
  ollama: 'Ollama Cloud',
};

const PROVIDER_DESCRIPTIONS: Record<LLMProvider, string> = {
  openai: 'GPT-4 and GPT-4o models for development scenario analysis.',
  anthropic: 'Claude models with strong analytical and reasoning capabilities.',
  google: 'Gemini models with multimodal understanding.',
  ollama: 'Open-source models hosted on Ollama Cloud infrastructure.',
};

export default function SettingsPage() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState<LLMSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<LLMProvider | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('');

  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getLLMSettings();
      setSettings(data);
      setSelectedProvider(data.active_provider);
      const active = data.providers.find((p) => p.provider === data.active_provider);
      if (active) setSelectedModel(active.model);
    } catch {
      setError('Failed to load LLM settings.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const handleProviderSelect = (provider: LLMProvider) => {
    setSelectedProvider(provider);
    setSuccessMsg(null);
    const config = settings?.providers.find((p) => p.provider === provider);
    if (config) setSelectedModel(config.model);
  };

  const handleSave = async () => {
    if (!selectedProvider) return;
    setSaving(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const updated = await updateLLMSettings({
        provider: selectedProvider,
        model: selectedModel || undefined,
      });
      setSettings(updated);
      setSuccessMsg('Settings saved successfully.');
    } catch {
      setError('Failed to save settings.');
    } finally {
      setSaving(false);
    }
  };

  const activeProviderConfig: LLMProviderConfig | undefined = settings?.providers.find(
    (p) => p.provider === selectedProvider
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-primary-900 text-white px-6 py-3 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold tracking-tight">RealtorDevOpsAI</h1>
          <span className="text-primary-300 text-sm">Settings</span>
        </div>
        <button
          onClick={() => navigate('/')}
          className="text-sm bg-primary-700 hover:bg-primary-600 px-3 py-1 rounded transition-colors"
        >
          Back to Analysis
        </button>
      </header>

      <main className="max-w-4xl mx-auto py-8 px-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">LLM Provider Settings</h2>
        <p className="text-gray-600 mb-8">
          Choose the AI model provider used for development scenario analysis.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}
        {successMsg && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
            {successMsg}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {settings?.providers.map((provider) => (
            <button
              key={provider.provider}
              onClick={() => handleProviderSelect(provider.provider)}
              className={`relative p-5 rounded-lg border-2 text-left transition-all ${
                selectedProvider === provider.provider
                  ? 'border-primary-600 bg-primary-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
              }`}
            >
              {settings.active_provider === provider.provider && (
                <span className="absolute top-3 right-3 text-xs font-medium bg-primary-100 text-primary-800 px-2 py-0.5 rounded-full">
                  Active
                </span>
              )}
              <div className="font-semibold text-gray-900 text-lg mb-1">
                {PROVIDER_ICONS[provider.provider]}
              </div>
              <p className="text-sm text-gray-500 mb-3">
                {PROVIDER_DESCRIPTIONS[provider.provider]}
              </p>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">Model:</span>
                <span className="text-xs font-mono text-gray-700 bg-gray-100 px-2 py-0.5 rounded">
                  {provider.model}
                </span>
              </div>
              <div className="mt-2">
                {provider.is_configured ? (
                  <span className="inline-flex items-center text-xs text-green-700 bg-green-50 px-2 py-0.5 rounded-full">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5" />
                    Configured
                  </span>
                ) : (
                  <span className="inline-flex items-center text-xs text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full">
                    <span className="w-1.5 h-1.5 bg-amber-500 rounded-full mr-1.5" />
                    API key not set
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>

        {activeProviderConfig && (
          <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {PROVIDER_ICONS[activeProviderConfig.provider]} Configuration
            </h3>

            <label className="block text-sm font-medium text-gray-700 mb-2">Model</label>
            <select
              value={selectedModel}
              onChange={(e) => {
                setSelectedModel(e.target.value);
                setSuccessMsg(null);
              }}
              className="w-full max-w-md rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            >
              {activeProviderConfig.available_models.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>

            {!activeProviderConfig.is_configured && (
              <p className="mt-4 text-sm text-amber-600">
                Set the API key in your backend <code className="bg-gray-100 px-1 rounded">.env</code> file to use this provider.
              </p>
            )}
          </div>
        )}

        <div className="flex items-center gap-4">
          <button
            onClick={handleSave}
            disabled={saving || !selectedProvider}
            className="px-6 py-2 bg-primary-700 text-white rounded-md font-medium text-sm hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 text-gray-600 border border-gray-300 rounded-md font-medium text-sm hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        </div>
      </main>
    </div>
  );
}

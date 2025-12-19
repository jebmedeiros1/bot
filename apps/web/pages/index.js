import { useState } from 'react'

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const Card = ({ title, children }) => (
  <div className="glass-card rounded-3xl p-6 flex-1 min-w-[280px] border border-white/50">
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-lg font-semibold text-purplePrimary">{title}</h3>
      <span className="h-2 w-2 rounded-full bg-purplePrimary animate-pulse"></span>
    </div>
    {children}
  </div>
)

export default function Home() {
  const [token, setToken] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [tenantName, setTenantName] = useState('')
  const [status, setStatus] = useState('')
  const [instanceId, setInstanceId] = useState('')
  const [providerSecret, setProviderSecret] = useState('')
  const [redisUrl, setRedisUrl] = useState('')

  const callApi = async (path, options = {}) => {
    const res = await fetch(`${apiUrl}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  }

  const register = async () => {
    try {
      const data = await callApi('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password, tenant_name: tenantName }),
      })
      setToken(data.access_token)
      setStatus('Registered and logged in')
    } catch (err) {
      setStatus(err.message)
    }
  }

  const createInstance = async () => {
    try {
      const data = await callApi('/evo/instances', { method: 'POST' })
      setInstanceId(data.id)
      setStatus('Evolution instance ready')
    } catch (err) {
      setStatus(err.message)
    }
  }

  const saveProvider = async () => {
    try {
      await callApi('/providers/1', {
        method: 'PUT',
        body: JSON.stringify({ provider_id: 1, kind: 'openai', display_name: 'OpenAI', secret: providerSecret }),
      })
      setStatus('Provider saved')
    } catch (err) {
      setStatus(err.message)
    }
  }

  const saveRedis = async () => {
    try {
      await callApi('/memory/redis', {
        method: 'PUT',
        body: JSON.stringify({ url: redisUrl, namespace: 'default' }),
      })
      setStatus('Redis connected')
    } catch (err) {
      setStatus(err.message)
    }
  }

  return (
    <div className="min-h-screen py-10 px-6">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="text-center">
          <p className="uppercase tracking-[0.2em] text-purplePrimary font-semibold">Evolution + OpenAI</p>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mt-2">Purple multi-tenant console</h1>
          <p className="text-slate-600 mt-3">Spin up Evolution, pair WhatsApp, configure bots, and ship replies with Redis-backed memory.</p>
        </header>

        <div className="grid gap-4 md:grid-cols-2">
          <Card title="1) Sign up">
            <div className="space-y-3">
              <input className="w-full rounded-xl border border-purple-100 p-3" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <input className="w-full rounded-xl border border-purple-100 p-3" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              <input className="w-full rounded-xl border border-purple-100 p-3" placeholder="Tenant name" value={tenantName} onChange={(e) => setTenantName(e.target.value)} />
              <button onClick={register} className="w-full bg-purplePrimary text-white rounded-xl py-3 font-semibold shadow-lg shadow-purplePrimary/30">Create tenant</button>
              <p className="text-xs text-slate-500">JWT stored in memory for demo. Use your own auth flow in production.</p>
            </div>
          </Card>

          <Card title="2) Evolution instance">
            <div className="space-y-3">
              <button onClick={createInstance} className="w-full bg-white text-purplePrimary border border-purplePrimary rounded-xl py-3 font-semibold shadow">Provision + get QR</button>
              {instanceId && <p className="text-sm text-slate-600">Instance created: #{instanceId}. Check QR via /evo/instances/{{id}}/qr.</p>}
              <p className="text-xs text-slate-500">Webhook pre-configured to {apiUrl}/webhooks/evolution/global</p>
            </div>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card title="Bot provider">
            <div className="space-y-3">
              <input className="w-full rounded-xl border border-purple-100 p-3" placeholder="OpenAI API key" value={providerSecret} onChange={(e) => setProviderSecret(e.target.value)} />
              <button onClick={saveProvider} className="w-full bg-purplePrimary text-white rounded-xl py-3 font-semibold shadow-lg shadow-purplePrimary/30">Save provider</button>
              <p className="text-xs text-slate-500">Secrets stored encrypted with AES-GCM.</p>
            </div>
          </Card>

          <Card title="Redis memory">
            <div className="space-y-3">
              <input className="w-full rounded-xl border border-purple-100 p-3" placeholder="redis://localhost:6379/0" value={redisUrl} onChange={(e) => setRedisUrl(e.target.value)} />
              <button onClick={saveRedis} className="w-full bg-white text-purplePrimary border border-purplePrimary rounded-xl py-3 font-semibold shadow">Save + test</button>
              <p className="text-xs text-slate-500">Use per-tenant namespaces for isolation.</p>
            </div>
          </Card>

          <Card title="Activity">
            <div className="space-y-2 text-sm text-slate-600">
              <p>• Monitor inbound webhooks and auto-replies.</p>
              <p>• Track QR pairing status.</p>
              <p>• See provider latency and token usage.</p>
            </div>
          </Card>
        </div>

        <footer className="text-center text-sm text-slate-500">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-50 text-purplePrimary font-semibold">Purple, playful & secure.</div>
          <div className="mt-2">Status: {status || 'awaiting action'}</div>
        </footer>
      </div>
    </div>
  )
}

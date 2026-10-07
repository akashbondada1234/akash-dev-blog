import { useState } from 'react';
import { Bot, Send } from 'lucide-react';
import { api } from '../services/api';

export default function ArticleAssistant({ content }) {
  const [question, setQuestion] = useState(''), [answer, setAnswer] = useState(''), [busy, setBusy] = useState(false);
  const ask = async (event) => { event.preventDefault(); if (!question.trim()) return; setBusy(true); try { setAnswer((await api.post('/ai/ask', { question, content })).answer); } catch (error) { setAnswer(error.message); } finally { setBusy(false); } };
  return <section className="mt-14 rounded-2xl border border-blue-200 bg-blue-50 p-6 dark:border-blue-900 dark:bg-[#172c3d]"><div className="flex items-center gap-2 font-semibold text-blue-700 dark:text-blue-300"><Bot size={19} /> Ask this article</div><p className="mt-2 text-sm text-gray-500 dark:text-gray-300">Ask a question and get an answer based only on this article.</p><form onSubmit={ask} className="mt-4 flex gap-2"><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What is the main idea?" className="min-w-0 flex-1 rounded-xl border-0 bg-white px-4 py-3 text-sm outline-none dark:bg-[#1d2d23] dark:text-white" /><button disabled={busy} className="rounded-xl bg-blue-500 px-4 text-white disabled:opacity-50"><Send size={17} /></button></form>{answer && <div className="mt-4 rounded-xl bg-white p-4 text-sm leading-6 text-gray-700 dark:bg-[#1d2d23] dark:text-gray-200">{answer}</div>}</section>;
}

import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Check, Clock, Copy, Share2 } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api } from '../services/api';
import Loading from '../components/Loading';
import PostCard from '../components/PostCard';
import ArticleAssistant from '../components/ArticleAssistant';
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function slugHeading(value) { return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''); }

export default function PostPage() {
  const { slug } = useParams();
  const [post, setPost] = useState(null), [related, setRelated] = useState([]), [copied, setCopied] = useState(false), [progress, setProgress] = useState(0);
  useEffect(() => {
    const onScroll = () => { const max = document.documentElement.scrollHeight - window.innerHeight; setProgress(max ? Math.round((window.scrollY / max) * 100) : 0); };
    window.addEventListener('scroll', onScroll); return () => window.removeEventListener('scroll', onScroll);
  }, []);
  useEffect(() => { setPost(null); api.get('/posts/' + slug).then((item) => { setPost(item); return api.get(`/posts?category=${item.category.id}&limit=4`); }).then((data) => setRelated(data.items.filter((item) => item.slug !== slug))).catch(() => setPost(false)); }, [slug]);
  const headings = useMemo(() => post?.content?.split('\n').filter((line) => line.startsWith('#')).map((line) => { const text = line.replace(/^#+\s*/, ''); return { text, id: slugHeading(text) }; }) || [], [post]);
  const share = async () => { try { await navigator.clipboard.writeText(window.location.href); setCopied(true); setTimeout(() => setCopied(false), 1800); } catch { window.prompt('Copy this link:', window.location.href); } };
  if (post === null) return <Loading />;
  if (!post) return <div className="mx-auto max-w-3xl px-5 py-28 text-center"><h1 className="serif text-4xl">Story not found</h1><Link className="mt-5 inline-block text-blue-500" to="/">Back home</Link></div>;
  return <main><div className="fixed left-0 top-0 z-30 h-1 bg-blue-500 transition-all" style={{ width: `${progress}%` }} /><article className="mx-auto max-w-5xl px-5 pb-20 pt-12"><Link to="/" className="mb-10 flex items-center gap-2 text-sm font-semibold text-blue-600"><ArrowLeft size={16} /> Back to stories</Link><div className="grid gap-12 md:grid-cols-[1fr_240px]"><div><span className="rounded-full bg-sage px-3 py-1 text-xs font-bold text-moss">{post.category.name}</span><h1 className="serif mt-6 text-5xl leading-tight text-ink md:text-7xl dark:text-white">{post.title}</h1><p className="mt-6 text-xl leading-8 text-gray-500 dark:text-gray-300">{post.excerpt}</p><div className="my-8 flex flex-wrap items-center gap-4 border-y border-[#e0e8df] py-5"><span className="grid h-10 w-10 place-items-center rounded-full bg-sage font-semibold text-moss">{post.author.name[0]}</span><div><b className="block text-sm dark:text-white">{post.author.name}</b><span className="text-xs text-gray-500">{new Date(post.created_at).toLocaleDateString()} · <Clock className="inline" size={12} /> 5 min read</span></div><button onClick={share} className="ml-auto flex items-center gap-2 rounded-full border border-[#dce5dc] px-4 py-2 text-sm font-semibold text-blue-600">{copied ? <Check size={15} /> : <Share2 size={15} />} {copied ? 'Copied' : 'Share'}</button></div>{post.cover_image && <img src={post.cover_image.startsWith('http') ? post.cover_image : API + post.cover_image} alt={post.title} className="mb-10 max-h-[480px] w-full rounded-2xl object-cover" loading="lazy" />}<div className="prose max-w-none text-lg text-gray-700 dark:text-gray-200"><ReactMarkdown remarkPlugins={[remarkGfm]} components={{ h2: ({ children }) => <h2 id={slugHeading(String(children))}>{children}</h2>, h3: ({ children }) => <h3 id={slugHeading(String(children))}>{children}</h3>, code: ({ inline, children }) => <code className={inline ? 'rounded bg-sage px-1 text-sm text-moss' : 'block overflow-x-auto rounded-xl bg-[#101a14] p-5 text-sm text-emerald-200'}><span className="group relative">{children}{!inline && <button onClick={() => navigator.clipboard?.writeText(String(children))} className="float-right rounded bg-white/10 px-2 py-1 text-xs text-white"><Copy size={13} /></button>}</span></code> }}>{post.content}</ReactMarkdown></div></div><aside className="hidden md:block"><div className="sticky top-28 rounded-2xl border border-[#dce5dc] bg-white p-5 dark:border-[#304638] dark:bg-[#1d2d23]"><p className="mb-4 text-xs font-bold uppercase tracking-widest text-blue-500">On this page</p>{headings.length ? headings.map((heading) => <a key={heading.id} href={'#' + heading.id} className="mb-3 block text-sm text-gray-500 hover:text-blue-500">{heading.text}</a>) : <p className="text-sm text-gray-500">A focused read.</p>}</div></aside></div></article>{related.length > 0 && <section className="border-t border-[#e0e8df] bg-white py-14 dark:bg-[#19271e]"><div className="mx-auto max-w-6xl px-5"><h2 className="serif mb-7 text-3xl dark:text-white">Keep exploring</h2><div className="grid gap-6 md:grid-cols-3">{related.slice(0, 3).map((item, index) => <PostCard key={item.id} post={item} index={index} />)}</div></div></section>}</main>;
}

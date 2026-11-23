import SocialLinks from './SocialLinks';

export default function Footer() {
  return <footer className="border-t border-[#d8dfd4] bg-[#f0eadb] py-10 dark:border-[#45634e] dark:bg-[#142019]">
    <div className="mx-auto flex max-w-6xl flex-col gap-7 px-5 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p className="serif text-2xl text-ink dark:text-white">akash<span className="text-blue-500">.journal</span></p>
        <p className="mt-2 max-w-sm text-sm leading-6 text-gray-600 dark:text-gray-400">Practical notes on building, debugging, and learning software in public.</p>
        <p className="mt-4 text-xs text-gray-500 dark:text-gray-500">© {new Date().getFullYear()} Akash Bondada. All rights reserved.</p>
      </div>
      <div className="flex flex-col gap-4 sm:items-end">
        <nav className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-300">
          <a href="/#journal" className="hover:text-moss">Journal</a>
          <a href="/#about" className="hover:text-moss">About</a>
          <a href="/#work" className="hover:text-moss">Projects</a>
          <a href="/#contact" className="hover:text-moss">Contact</a>
        </nav>
        <SocialLinks />
      </div>
    </div>
  </footer>;
}

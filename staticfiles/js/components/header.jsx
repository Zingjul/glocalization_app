function Header({ isAuthenticated }) {
    const [open, setOpen] = React.useState(false);
    return (
      <header className="bg-light from-gray-900 to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Brand / Logo */}
            <a href="/" className="text-3xl tracking-tight text-blue-400 hover:text-blue-600 transition-colors duration-200" style={{ fontFamily: "'Montserrat', 'Open Sans', Arial, sans-serif" }}>
              My Website
            </a>
  
            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <a href="/" className="text-black-300 hover:text-blue-400 font-medium px-3 py-2 rounded transition">Home</a>
                  <a href="/logout" className="text-gray-100 hover:text-blue-400 font-medium px-3 py-2 rounded transition">Logout</a>
                  <a href="/delete_account" className="bg-transparent border border-red-600 text-red-600 hover:bg-red-600 hover:text-white font-semibold px-4 py-2 rounded-lg transition">Delete Account</a>
                </>
              ) : (
                <>
                  <a href="/signup" className="text-gray-100 hover:text-blue-400 font-medium px-3 py-2 rounded transition">Sign up</a>
                  <a href="/login" className="text-gray-100 hover:text-blue-400 font-medium px-3 py-2 rounded transition">Login</a>
                </>
              )}
            </nav>
  
            {/* Mobile menu button */}
            <div className="md:hidden flex items-center">
              <button
                className="text-gray-100 hover:text-blue-400 focus:outline-none"
                aria-label="Open menu"
                onClick={() => setOpen(o => !o)}
              >
                <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {open ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 8h16M4 16h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>
        </div>
        {/* Mobile Dropdown */}
        {open && (
          <div className="md:hidden px-2 pt-2 pb-3 space-y-1 bg-gray-900 border-t border-gray-800 shadow">
            {isAuthenticated ? (
              <>
                <a href="/" className="block text-gray-100 hover:text-blue-400 font-medium px-3 py-2 rounded transition" onClick={() => setOpen(false)}>Home</a>
                <a href="/logout" className="block text-gray-100 hover:text-blue-400 font-medium px-3 py-2 rounded transition" onClick={() => setOpen(false)}>Logout</a>
                <a href="/delete_account" className="block border border-red-600 text-red-600 hover:bg-red-600 hover:text-white font-semibold px-4 py-2 rounded-lg transition" onClick={() => setOpen(false)}>Delete Account</a>
              </>
            ) : (
              <>
                <a href="/signup" className="block text-gray-100 hover:text-blue-400 font-medium px-3 py-2 rounded transition" onClick={() => setOpen(false)}>Sign up</a>
                <a href="/login" className="block text-gray-100 hover:text-blue-400 font-medium px-3 py-2 rounded transition" onClick={() => setOpen(false)}>Login</a>
              </>
            )}
          </div>
        )}
      </header>
    );
  }
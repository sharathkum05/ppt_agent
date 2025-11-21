function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-xl p-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Tailwind Test
        </h1>
        <p className="text-gray-600">
          If you see colors, gradients, and styling, Tailwind is working!
        </p>
        <button className="mt-4 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">
          Test Button
        </button>
      </div>
    </div>
  )
}

export default App

import './App.css'
import { Tweet } from './components/Tweet.tsx'

function App() {
  return (
	<main>
		<h1>Feed</h1>
		<Tweet author="edu" text="Mi tweet" includePics={false} />
	</main>
  )
}

export default App

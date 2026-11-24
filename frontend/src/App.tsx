import './App.css'
import { Tweet } from './components/Tweet.tsx'

function App() {
  return (
	<main>
		<h1 style={{textAlign: "center"}}>Feed</h1>
		<Tweet author="edu" text="Mi tweet" includePics={false} likes={0} likedByMe={false} />
		<Tweet author="edu" text="Mi tweet" includePics={false} likes={3} likedByMe={false} />
		<Tweet author="edu" text="Mi tweet" includePics={false} likes={5} likedByMe={true} />
		<Tweet author="edu" text="Mi tweet" includePics={false} likes={1} likedByMe={true} />
		<Tweet author="edu" text="Mi tweet" includePics={false} likes={42} likedByMe={false} />
	</main>
  )
}

export default App

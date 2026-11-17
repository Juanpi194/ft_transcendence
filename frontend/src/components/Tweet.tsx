type TweetProps =  {
	author: string
	text: string
	includePics: boolean
}

export function Tweet({author, text}: TweetProps)
{
	return (
		<article className="tweet">
			<strong>@{author}</strong>
			<p>{text}</p>
		</article>
	)
}

import { useState } from "react";

type TweetProps =  {
	author: string
	text: string
	includePics: boolean
	likes: number
	likedByMe: boolean
}

type LikeButtonProps = {
	initialLiked: boolean
	initialLikes: number
}

function LikeButton({initialLiked, initialLikes}: LikeButtonProps)
{
	const [liked, setLiked] = useState(initialLiked);

	// Likes de los demás: el total que llega, quitando el mío si ya lo había dado
	const othersLikes = initialLikes - (initialLiked ? 1 : 0);
	// Esto no es estado: se recalcula en cada render a partir de `liked`
	const likes = othersLikes + (liked ? 1 : 0);

	function handleClick()
	{
		setLiked(prev => !prev);
	}

	return (
		<button
			type="button"
			className="like-button"
			aria-pressed={liked}
			onClick={handleClick}
		>
			{liked ? "Dislaik" : "Like"} · {likes}
		</button>
	)
}

export function Tweet({author, text, likes, likedByMe}: TweetProps)
{
	return (
		<article className="tweet">
			<strong>@{author}</strong>
			<p>{text}</p>
			<LikeButton initialLiked={likedByMe} initialLikes={likes} />
		</article>
	)
}

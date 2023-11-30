import { useState } from 'preact/hooks';

export default function Snack({messages}) {

  const randomMessage = () => messages[(Math.floor(Math.random() * messages.length))];

  const [greeting, setGreeting] = useState(messages[0]);

  return (
    <div>
      <h3>{greeting}! Thank you for visiting!</h3>
      <button onClick={() => setGreeting(randomMessage())}>
        New Greeting
      </button>
    </div>
  );
}


var snack = document.getElementById("snackbar");
snack.innerHTML = "";
console.log(data["detail"]);
snack.innerHTML += data["detail"];
snack.className = "show";
setTimeout(function(){ snack.className = snack.className.replace("show", ""); }, 3000);
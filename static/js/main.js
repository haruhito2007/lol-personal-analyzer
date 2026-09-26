console.log("JavaScript loaded")

const form = document.getElementById("search-form");

form.addEventListener("submit",function(event) {
  event.preventDefault();

  const gameName = document.getElementById("game-name").value;
  const tagline = document.getElementById("tag-line").value;

  console.log(gameName);
  console.log(tagline);
});

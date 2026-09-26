console.log("JavaScript loaded")

const form = document.getElementById("search-form");

form.addEventListener("submit",function(event) {
  event.preventDefault();

  const gameName = document.getElementById("game-name").value;
  const tagline = document.getElementById("tag-line").value;

  console.log(gameName);
  console.log(tagline);

  fetch("/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      gameName: gameName,
      tagline: tagline
    })
  })
  .then(function(response) {
    return response.json();
  })
  .then(function(data) {
    console.log(data);
  });
});
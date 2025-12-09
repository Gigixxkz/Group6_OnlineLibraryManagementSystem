const bellBtn = document.getElementById("bellBtn");
const bellMenu = document.getElementById("bellMenu");

if (bellBtn && bellMenu) {
  bellBtn.addEventListener("click", () => {
    bellMenu.style.display = bellMenu.style.display === "none" ? "block" : "none";
  });
}
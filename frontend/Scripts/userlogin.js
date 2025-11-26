//----------------------------------------------------------------------------
//File: userlogin.js
//Created by: Georgia Kazara
//Course: Software Engineering II
//Project: Online Library Management System (Group 6)
//Description: Handles the user login on the frontend by sending the 
//             entered credentials to the backend for verification.
//Date Created: 19 November 2025
//Last Updated: 19 November 2025
//----------------------------------------------------------------------------

//Waiting until the whole page is fully loaded
document.addEventListener("DOMContentLoaded", () => {

    //Getting the login form
    const form = document.querySelector("form");

    //When the user clicks the Login button:
    form.addEventListener("submit", async (e) => {
        e.preventDefault();   //We stop the page from refreshing

        //Geting whatever the user inserted in the fields
        const usernameOrEmail = document.getElementById("usernameOrEmail").value;
        const password = document.getElementById("password").value;

        //Sending the login stuff to the backend
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
                username_or_email: usernameOrEmail,
                password: password
            })
        });

        //If the backend says login is correct then we go to the homepage!!!
        if (response.ok) {
            window.location.href = "/static/HTML/HomePage.html";
        } 
        //If login is wrong then we show an error message!!!
        else {
            alert("Wrong username/email or password.");
        }
    });
});
//----------------------------------------------------------------------------
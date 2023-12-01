let tokenToSend = `${localStorage.getItem("SavedToken")}`;
    
      fetch('http://127.0.0.1:8000/me', {
        credentials: "same-origin",
        method: 'GET',
        headers: {
          'accept': 'application/json',
          'Authorization': tokenToSend
        },

      }).then(response => 
       {
        if (response.status == 401) {
              response.json().then(data => {
                console.log(tokenToSend);
                window.location.href = "/login-page";
              });
        }});
// function to handle login
function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
  
    if (!username || !password) {
      alert('Please enter both username and password.');
      return;
    }
    
    fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Login failed');
        }
        return response.json();
      })
      .then((data) => {
        alert('Login successful!');
        window.location.reload(); // reloading will direct user to the home page 
      })
      .catch((error) => {
        alert('Invalid credentials, please try again.');
        console.error('Error:', error);
      });
  }
  
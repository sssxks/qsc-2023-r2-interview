import requests
import bs4

class PasswordError(Exception):
    """Custom exception class for password-related errors during login."""

    def __init__(self, message):
        """
        Initialize a PasswordError instance with a custom error message.

        Args:
            message (str): A descriptive error message.
        """
        super().__init__(message)


class ZJUSession(requests.Session):
    """This class offers ZJU authentication system login ability to requests.Session."""
    def __init__(self, username, password) -> None:
        """Initialize a ZJUSession object for logging in to Zhejiang University's authentication system (zjuam).

        Args:
            username (str): Your ZJU username.
            password (str): Your ZJU password.
        
        Raises:
            PasswordError: If a incorrect password is provided.
            requests.exceptions.RequestException: If a network error occurs during the login process.
            KeyError: If the expected HTML elements or JSON fields are not found.
            ValueError: If there are issues with JSON decoding.

        """
        super().__init__()
        
        self.username = username
        self.password = password
        
        self.login()
        
    def login(self):
        """Log in to Zhejiang University's authentication system (zjuam).

        Raises:
            PasswordError: If a incorrect password is provided.
            requests.exceptions.RequestException: If a network error occurs during the login process.
            KeyError: If the expected HTML elements or JSON fields are not found.
            ValueError: If there are issues with JSON decoding.
            
        """
        # Step 1: GET the login page to obtain cookies, _event_id, and execution values
        login_page_response = self.get('https://zjuam.zju.edu.cn/cas/login')
        login_page_response.raise_for_status()
        soup = bs4.BeautifulSoup(login_page_response.content, features="html.parser")
        event_id = soup.find('input', attrs={'type':'hidden','name':'_eventId'})['value']
        execution = soup.find('input', attrs={'type':'hidden','name':'execution'})['value']
        
        # Step 2: GET the public key needed to encrypt the password
        pub_key_response = self.get('https://zjuam.zju.edu.cn/cas/v2/getPubKey')
        pub_key_response.raise_for_status()
        pub_key = pub_key_response.json()
        
        # Step 3: Encrypt the password using the JavaScript library
        encrypted_password = requests.post('http://localhost:48218/api/encrypt',
                                        json={"exponent":pub_key['exponent'],
                                                "modulus":pub_key['modulus'],
                                                "password":self.password[::-1]
                                                }
                                        ).json()['crypt']

        # Step 4: POST the login request with the encrypted password
        login_response = self.post('https://zjuam.zju.edu.cn/cas/login',data={
                'username': self.username,
                'password': encrypted_password,
                'authcode': '',
                'execution' :execution,
                '_eventId': event_id
            }, allow_redirects=False)
        login_response.raise_for_status()
        if "密码错误" in login_response.content.decode():
            raise PasswordError('Password not correct!')
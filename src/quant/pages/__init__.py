from pages.backtesting import BackTestingManager
from pages.login import LoginManager

# display order
pages = {
    LoginManager.name: LoginManager(),
    BackTestingManager.name: BackTestingManager(),
}

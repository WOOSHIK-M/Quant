from src.pages.backtesting import BackTestingManager
from src.pages.login import LoginManager

# display order
pages = {
    LoginManager.name: LoginManager(),
    BackTestingManager.name: BackTestingManager(),
}

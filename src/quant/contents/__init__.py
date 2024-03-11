from contents.backtesting import BackTestingManager
from contents.login import LoginManager

# display order
pages = {
    LoginManager.name: LoginManager(),
    BackTestingManager.name: BackTestingManager(),
}

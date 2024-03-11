from contents.backtesting import BackTestingManager
from contents.login import LoginManager

# display order
contents = {
    LoginManager.name: LoginManager(),
    BackTestingManager.name: BackTestingManager(),
}

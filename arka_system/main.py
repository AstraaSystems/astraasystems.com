# arka_system/main.py
from core.executive import Arka
from core.kernel import ArdhanarishvaraOS
from portfolio.selector import PortfolioSelector
from portfolio.strategy import StrategyMode
from gateways.nifty_gateway import NiftyGateway

def build_sovereign_system():
    # 1. Initialize OS Kernel
    os_kernel = ArdhanarishvaraOS()
    
    # 2. Initialize Executive with desired mode
    arka = Arka(os_kernel, mode=StrategyMode.GROWTH)
    
    # 3. Attach Portfolio tools
    selector = PortfolioSelector()
    
    return arka, os_kernel, selector
# arka_system/main.py
from core.executive import Arka
from core.kernel import ArdhanarishvaraOS
from portfolio.strategy import StrategyMode
from gateways.nifty_gateway import NiftyGateway

def boot():
    os_kernel = ArdhanarishvaraOS()
    arka = Arka(os_kernel, mode=StrategyMode.GROWTH)
    nifty = NiftyGateway(api_key="sk_live_arka_v300")
    
    print("Sovereign Architecture: Online")
    return arka, nifty

if __name__ == "__main__":
    arka, nifty = boot()
    arka, os, selector = build_sovereign_system()
    print("Sovereign Architecture Initialized. Systems Nominal.")

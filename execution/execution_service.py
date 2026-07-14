# ====================================
# execution_service.py
# ====================================

import time

from storage.order_repository import (
    OrderRepository
)

from storage.fill_repository import (
    FillRepository
)

from storage.position_repository import (
    PositionRepository
)

from storage.execution_repository import (
    ExecutionRepository
)

from execution.execution_scheduler import (
    ExecutionScheduler
)

from execution.fill_tracker import (
    FillTracker
)

from execution.execution_log import (
    ExecutionAuditLogger
)

from analytics.slippage_analyzer import (
    SlippageAnalyzer
)

from analytics.pnl_tracker import (
    PnLTracker
)

from data.market_event_bus import (
    MarketEventBus
)

from risk.risk_manager import (
    RiskManager
)

from risk.liquidity_monitor import (
    LiquidityMonitor
)

from core.market_state import (
    MarketState
)

from core.redis_state import (
    RedisState
)

from portfolio.position_manager import (
    PositionManager
)

from strategies.twap import (
    TWAPStrategy
)

from strategies.adaptive_vwap import (
    AdaptiveVWAPStrategy
)

from strategies.pov import (
    POVStrategy
)

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_timestamp
)

from utils.constants import (

    TWAP,

    VWAP,

    POV,

    RUNNING,

    HALTED,

    COMPLETED,

    ORDER_FILLED_EVENT,

    EXECUTION_STARTED,

    EXECUTION_COMPLETED,

    MARKET_UPDATE_EVENT,

    PARENT_ORDER_SPLIT,

    PARENT_ORDER_PROGRESS,

    PARENT_ORDER_COMPLETED,

    PARENT_ORDER_HALTED
)

from utils.config import (

    EXECUTION_INTERVAL,

    DEFAULT_PARTICIPATION
)


class ExecutionService:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        market_state=None,

        event_bus=None,

        oms=None,

        position_manager=None,

        market_data_service=None
    ):

        self.logger = (
            SystemLogger()
        )

        self.execution_file_logger = (
            SystemLogger(
                log_type="execution"
            )
        )

        self.order_repository = (
            OrderRepository()
        )

        self.fill_repository = (
            FillRepository()
        )

        self.position_repository = (
            PositionRepository()
        )

        self.execution_repository = (
            ExecutionRepository()
        )

        self.redis_state = (
            RedisState()
        )

        self.market_state = (

            market_state
            if market_state
            else MarketState()
        )

        self.market_data_service = (
            market_data_service
        )

        self.event_bus = (

            event_bus
            if event_bus
            else MarketEventBus()
        )

        if oms is None:

            raise RuntimeError(
                "OMS dependency required"
            )

        self.oms = oms

        self.position_manager = (

            position_manager
            if position_manager
            else PositionManager()
        )

        self.execution_logger = (
            ExecutionAuditLogger()
        )

        self.fill_tracker = (
            FillTracker()
        )

        self.slippage_analyzer = (
            SlippageAnalyzer()
        )

        self.pnl_tracker = (
            PnLTracker()
        )

        self.risk_manager = (

            RiskManager(

                market_state=
                self.market_state
            )
        )

        self.liquidity_monitor = (

            LiquidityMonitor(

                market_state=
                self.market_state
            )
        )

        self.active_orders = {}

        self.status = RUNNING

        self.last_child_failure_reason = None

        self.event_bus.subscribe(

            MARKET_UPDATE_EVENT,

            self.on_market_update
        )

        self.logger.info(
            "Execution Service Initialized"
        )


    # ====================================
    # MARKET UPDATE
    # ====================================

    def on_market_update(

        self,

        market_event
    ):

        try:

            self.logger.info(

                f"Market Update | "
                f"{market_event.get('symbol')} | "
                f"{market_event.get('price')}"
            )

        except Exception as error:

            self.logger.error(

                f"Market Update Failed | "
                f"{error}"
            )


    # ====================================
    # ENSURE MARKET DATA
    # ====================================

    def ensure_market_data(

        self,

        symbol,

        wait_seconds=3
    ):

        symbol = (
            symbol.upper()
        )

        if (

            self.market_data_service
            and
            hasattr(
                self.market_data_service,
                "subscribe"
            )
        ):

            self.market_data_service.subscribe(
                symbol
            )

        price = (

            self.market_state
            .get_price(
                symbol
            )
        )

        if price and price > 0:

            return price

        start_time = (
            time.time()
        )

        while (

            time.time()
            -
            start_time

        ) < wait_seconds:

            price = (

                self.market_state
                .get_price(
                    symbol
                )
            )

            if price and price > 0:

                return price

            time.sleep(
                0.25
            )

        raise RuntimeError(

            f"Market Price Unavailable | "
            f"{symbol}"
        )


    # ====================================
    # PUBLISH PARENT ORDER SPLIT
    # ====================================

    def publish_parent_order_split(

        self,

        parent_order,

        schedule
    ):

        total_children = len(
            schedule
        )

        self.event_bus.publish(

            PARENT_ORDER_SPLIT,

            {

                "parent_order_id":
                parent_order.order_id,

                "symbol":
                parent_order.symbol,

                "side":
                parent_order.side,

                "strategy":
                parent_order.strategy,

                "total_qty":
                parent_order.quantity,

                "total_children":
                total_children,

                "completed_children":
                0,

                "current_slice":
                0,

                "completion_pct":
                0,

                "status":
                "SPLIT",

                "message":
                "Parent order successfully split into child orders"
            }
        )


    # ====================================
    # PUBLISH PARENT ORDER PROGRESS
    # ====================================

    def publish_parent_order_progress(

        self,

        parent_order,

        progress
    ):

        self.event_bus.publish(

            PARENT_ORDER_PROGRESS,

            {

                "parent_order_id":
                parent_order.order_id,

                "symbol":
                parent_order.symbol,

                "side":
                parent_order.side,

                "strategy":
                parent_order.strategy,

                "total_qty":
                parent_order.quantity,

                "total_children":
                progress.get(
                    "total_slices",
                    0
                ),

                "completed_children":
                progress.get(
                    "completed_slices",
                    0
                ),

                "current_slice":
                progress.get(
                    "current_slice",
                    0
                ),

                "completion_pct":
                progress.get(
                    "completion_pct",
                    0
                ),

                "status":
                progress.get(
                    "status",
                    RUNNING
                ),

                "reason":
                progress.get(
                    "reason",
                    ""
                )
            }
        )


    # ====================================
    # PUBLISH PARENT ORDER COMPLETED
    # ====================================

    def publish_parent_order_completed(

        self,

        parent_order,

        total_children
    ):

        self.event_bus.publish(

            PARENT_ORDER_COMPLETED,

            {

                "parent_order_id":
                parent_order.order_id,

                "symbol":
                parent_order.symbol,

                "side":
                parent_order.side,

                "strategy":
                parent_order.strategy,

                "total_qty":
                parent_order.quantity,

                "total_children":
                total_children,

                "completed_children":
                total_children,

                "current_slice":
                total_children,

                "completion_pct":
                100,

                "status":
                COMPLETED
            }
        )


    # ====================================
    # PUBLISH PARENT ORDER HALTED
    # ====================================

    def publish_parent_order_halted(

        self,

        parent_order,

        scheduler_status,

        reason
    ):

        total_children = scheduler_status.get(
            "total_slices",
            0
        )

        completed_children = scheduler_status.get(
            "completed_slices",
            0
        )

        completion_pct = 0

        if total_children > 0:

            completion_pct = round(

                completed_children
                /
                total_children
                *
                100,

                2
            )

        self.event_bus.publish(

            PARENT_ORDER_HALTED,

            {

                "parent_order_id":
                parent_order.order_id,

                "symbol":
                parent_order.symbol,

                "side":
                parent_order.side,

                "strategy":
                parent_order.strategy,

                "total_qty":
                parent_order.quantity,

                "total_children":
                total_children,

                "completed_children":
                completed_children,

                "current_slice":
                scheduler_status.get(
                    "current_slice",
                    0
                ),

                "completion_pct":
                completion_pct,

                "status":
                HALTED,

                "reason":
                reason
            }
        )


    # ====================================
    # SUBMIT ORDER
    # ====================================

    def submit_order(

        self,

        parent_order
    ):

        try:

            parent_order.symbol = (
                parent_order.symbol.upper()
            )

            self.last_child_failure_reason = None

            arrival_price = (

                self.ensure_market_data(
                    parent_order.symbol
                )
            )

            if hasattr(
                parent_order,
                "arrival_price"
            ):

                parent_order.arrival_price = (
                    arrival_price
                )

            parent_order.start_order()

            self.order_repository.save_order(
                parent_order
            )

            self.active_orders[
                parent_order.order_id
            ] = parent_order

            self.execution_file_logger.info(

                f"Execution Started | "
                f"OrderID={parent_order.order_id} | "
                f"{parent_order.symbol} | "
                f"{parent_order.strategy} | "
                f"Qty={parent_order.quantity} | "
                f"Side={parent_order.side} | "
                f"ArrivalPrice={arrival_price}"
            )

            self.event_bus.publish(

                EXECUTION_STARTED,

                parent_order.get_snapshot()
            )

            strategy = (
                self.create_strategy(
                    parent_order
                )
            )

            # ====================================
            # GENERATE CHILD ORDER SCHEDULE
            # ====================================

            if hasattr(

                strategy,

                "generate_schedule"
            ):

                schedule = (
                    strategy.generate_schedule()
                )

            else:

                schedule = []

                while (

                    strategy.remaining_qty
                    >
                    0
                ):

                    next_order = (
                        strategy.get_next_order()
                    )

                    if next_order is None:

                        break

                    schedule.append(
                        next_order
                    )

            # ====================================
            # PUBLISH PARENT ORDER SPLIT
            # ====================================

            self.publish_parent_order_split(

                parent_order,

                schedule
            )

            # ====================================
            # RUN SCHEDULE
            # ====================================

            scheduler = (

                ExecutionScheduler(

                    execution_interval=
                    EXECUTION_INTERVAL,

                    market_state=
                    self.market_state
                )
            )

            scheduler_status = (

                scheduler.run_schedule(

                    schedule,

                    lambda child_order:
                    self.execute_child_order(

                        parent_order,

                        child_order
                    ),

                    progress_callback=
                    lambda progress:
                    self.publish_parent_order_progress(

                        parent_order,

                        progress
                    )
                )
            )

            # ====================================
            # HANDLE HALTED SCHEDULE
            # ====================================

            if scheduler_status.get(
                "status"
            ) == HALTED:

                halt_reason = (

                    self.last_child_failure_reason

                    or

                    scheduler_status.get(
                        "reason"
                    )

                    or

                    "Execution halted during child order schedule"
                )

                parent_order.halt_order(
                    halt_reason
                )

                self.order_repository.save_order(
                    parent_order
                )

                self.publish_parent_order_halted(

                    parent_order,

                    scheduler_status,

                    halt_reason
                )

                self.active_orders.pop(

                    parent_order.order_id,

                    None
                )

                return {

                    "status":
                    HALTED,

                    "order_id":
                    parent_order.order_id,

                    "reason":
                    halt_reason
                }

            # ====================================
            # COMPLETE PARENT ORDER
            # ====================================

            parent_order.complete_order()

            self.publish_parent_order_completed(

                parent_order,

                len(
                    schedule
                )
            )

            self.order_repository.save_order(
                parent_order
            )

            self.execution_repository.save_execution(

                parent_order.get_snapshot()
            )

            self.event_bus.publish(

                EXECUTION_COMPLETED,

                parent_order.get_snapshot()
            )

            self.active_orders.pop(

                parent_order.order_id,

                None
            )

            self.execution_file_logger.info(

                f"Execution Completed | "
                f"OrderID={parent_order.order_id} | "
                f"{parent_order.symbol}"
            )

            return {

                "status":
                COMPLETED,

                "order_id":
                parent_order.order_id
            }

        except Exception as error:

            try:

                parent_order.halt_order(
                    str(error)
                )

            except Exception:

                pass

            try:

                self.publish_parent_order_halted(

                    parent_order,

                    {

                        "total_slices":
                        0,

                        "completed_slices":
                        0,

                        "current_slice":
                        0
                    },

                    str(error)
                )

            except Exception:

                pass

            self.active_orders.pop(

                parent_order.order_id,

                None
            )

            self.logger.error(

                f"Execution Failed | "
                f"{error}"
            )

            return {

                "status":
                HALTED,

                "order_id":
                getattr(
                    parent_order,
                    "order_id",
                    None
                ),

                "reason":
                str(error)
            }


    # ====================================
    # EXECUTE CHILD ORDER
    # ====================================

    def execute_child_order(

        self,

        parent_order,

        child_order
    ):

        qty = (
            child_order[
                "qty"
            ]
        )

        symbol = (
            parent_order.symbol.upper()
        )

        arrival_price = (

            self.market_state
            .get_price(
                symbol
            )
        )

        if not arrival_price:

            self.last_child_failure_reason = (
                f"Market Price Missing | {symbol}"
            )

            self.logger.error(
                self.last_child_failure_reason
            )

            return False

        liquidity_result = (
            self.evaluate_liquidity(
                symbol
            )
        )

        if (

            liquidity_result
            and
            liquidity_result.get(
                "market_quality"
            ) == "POOR"
        ):

            self.last_child_failure_reason = (
                f"Liquidity Check Failed | {symbol}"
            )

            self.logger.warning(
                self.last_child_failure_reason
            )

            return False

        risk_ok = (

            self.validate_risk(

                symbol=
                symbol,

                qty=
                qty,

                current_position=
                getattr(
                    parent_order,
                    "filled_quantity",
                    0
                )
            )
        )

        if not risk_ok:

            self.last_child_failure_reason = (
                f"Risk Check Failed | {symbol}"
            )

            self.logger.warning(
                self.last_child_failure_reason
            )

            return False

        order = (

            self.oms.submit_market_order(

                symbol=
                symbol,

                qty=
                qty,

                side=
                parent_order.side
            )
        )

        if order is None:

            self.last_child_failure_reason = (
                f"OMS Submission Failed | {symbol}"
            )

            self.logger.error(
                self.last_child_failure_reason
            )

            return False

        fill_price = (

            self.extract_fill_price(

                order=
                order,

                fallback_price=
                arrival_price
            )
        )

        broker_order_id = (
            self.extract_order_id(
                order
            )
        )

        order_status = (
            self.extract_order_status(
                order
            )
        )

        parent_order.add_fill(

            fill_qty=
            qty,

            fill_price=
            fill_price
        )

        self.fill_tracker.record_fill(

            order_id=
            str(
                broker_order_id
            ),

            symbol=
            symbol,

            qty=
            qty,

            fill_price=
            fill_price,

            status=
            str(
                order_status
            ),

            side=
            parent_order.side,

            strategy=
            parent_order.strategy
        )

        self.fill_repository.save_fill(

            {

                "order_id":
                parent_order.order_id,

                "broker_order_id":
                str(
                    broker_order_id
                ),

                "symbol":
                symbol,

                "side":
                parent_order.side,

                "qty":
                qty,

                "fill_price":
                fill_price,

                "status":
                str(
                    order_status
                ),

                "strategy":
                parent_order.strategy,

                "timestamp":
                get_current_timestamp()
            }
        )

        self.position_manager.update_position(

            symbol=
            symbol,

            side=
            parent_order.side,

            qty=
            qty,

            fill_price=
            fill_price,

            market_price=
            arrival_price
        )

        updated_position = (

            self.position_manager
            .get_position(
                symbol
            )
        )

        if updated_position:

            self.position_repository.save_position(
                updated_position
            )

        self.event_bus.publish(

            ORDER_FILLED_EVENT,

            {

                "order_id":
                parent_order.order_id,

                "broker_order_id":
                str(
                    broker_order_id
                ),

                "symbol":
                symbol,

                "side":
                parent_order.side,

                "qty":
                qty,

                "fill_price":
                fill_price
            }
        )

        self.execution_file_logger.info(

            f"Child Order Executed | "
            f"ParentOrderID={parent_order.order_id} | "
            f"BrokerOrderID={broker_order_id} | "
            f"{symbol} | "
            f"Side={parent_order.side} | "
            f"Qty={qty} | "
            f"FillPrice={fill_price}"
        )

        return True


    # ====================================
    # EVALUATE LIQUIDITY
    # ====================================

    def evaluate_liquidity(

        self,

        symbol
    ):

        try:

            if hasattr(

                self.liquidity_monitor,

                "evaluate_market"
            ):

                try:

                    return (

                        self.liquidity_monitor
                        .evaluate_market(
                            symbol=symbol
                        )
                    )

                except TypeError:

                    return (

                        self.liquidity_monitor
                        .evaluate_market()
                    )

        except Exception as error:

            self.logger.error(

                f"Liquidity Evaluation Failed | "
                f"{error}"
            )

        return None


    # ====================================
    # VALIDATE RISK
    # ====================================

    def validate_risk(

        self,

        symbol,

        qty,

        current_position
    ):

        try:

            try:

                return (

                    self.risk_manager
                    .validate_order(

                        symbol=
                        symbol,

                        qty=
                        qty,

                        current_position=
                        current_position
                    )
                )

            except TypeError:

                return (

                    self.risk_manager
                    .validate_order(

                        qty=
                        qty,

                        current_position=
                        current_position
                    )
                )

        except Exception as error:

            self.logger.error(

                f"Risk Validation Failed | "
                f"{error}"
            )

            return False


    # ====================================
    # EXTRACT FILL PRICE
    # ====================================

    def extract_fill_price(

        self,

        order,

        fallback_price
    ):

        fill_price = getattr(

            order,

            "filled_avg_price",

            None
        )

        if fill_price is None and isinstance(
            order,
            dict
        ):

            fill_price = order.get(
                "filled_avg_price"
            )

        if fill_price:

            return float(
                fill_price
            )

        return float(
            fallback_price
        )


    # ====================================
    # EXTRACT ORDER ID
    # ====================================

    def extract_order_id(

        self,

        order
    ):

        order_id = getattr(

            order,

            "id",

            None
        )

        if order_id is None and isinstance(
            order,
            dict
        ):

            order_id = order.get(
                "id"
            )

        return order_id


    # ====================================
    # EXTRACT ORDER STATUS
    # ====================================

    def extract_order_status(

        self,

        order
    ):

        status = getattr(

            order,

            "status",

            None
        )

        if status is None and isinstance(
            order,
            dict
        ):

            status = order.get(
                "status"
            )

        return status


    # ====================================
    # CREATE STRATEGY
    # ====================================

    def create_strategy(

        self,

        parent_order
    ):

        if parent_order.strategy == TWAP:

            return TWAPStrategy(

                total_qty=
                parent_order.quantity,

                total_minutes=
                1,

                slices=
                5
            )

        elif parent_order.strategy == VWAP:

            return AdaptiveVWAPStrategy(

                total_qty=
                parent_order.quantity,

                target_participation=
                DEFAULT_PARTICIPATION,

                market_state=
                self.market_state
            )

        elif parent_order.strategy == POV:

            return POVStrategy(

                total_qty=
                parent_order.quantity
            )

        raise ValueError(

            f"Unsupported Strategy | "
            f"{parent_order.strategy}"
        )


    # ====================================
    # GET ACTIVE ORDERS
    # ====================================

    def get_active_orders(self):

        return {

            order_id:
            order.get_snapshot()

            for order_id, order

            in self.active_orders.items()
        }


    # ====================================
    # GET POSITIONS
    # ====================================

    def get_positions(self):

        return (

            self.position_manager
            .get_all_positions()
        )


    # ====================================
    # STOP EXECUTION
    # ====================================

    def stop(self):

        self.status = HALTED

        self.logger.warning(
            "Execution Service Halted"
        )
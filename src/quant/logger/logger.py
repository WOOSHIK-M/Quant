import logging


class LoggerFactory:
    """LoggerFactory is a factory class for creating logger instances."""

    @staticmethod
    def make_logger(name: str) -> logging.Logger:
        """Make a logger instance."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.StreamHandler()
            ]
        )

        # Create a logger instance
        logger = logging.getLogger(name)
        return logger

from rainpy.logger import set_logger


def test_logger_outputs():
    logger = set_logger(
        name="test_logger",
    )
    print("Testing logger outputs")
    logger.info("Testing logger outputs")
    logger.debug("Debug message for testing")
    logger.error("Error message for testing")
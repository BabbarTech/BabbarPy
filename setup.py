from setuptools import setup, find_packages
setup(
    name="BabbarPy",
    version="1.0.4",
    description="API routes for www.babbar.tech",
    author="Pierre Calvet",
    author_email="support@babbar.tech",
    license="MIT",
    Homepage = "https://github.com/BabbarTech/BabbarPy",
    packages=find_packages(),      
	  install_requires=[
          "requests",
           "pandas"]
)
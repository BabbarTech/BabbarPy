from setuptools import setup, find_packages
setup(
    name="BabbarPy",
      version="1.0.3",
      description="API routes for www.babbar.tech",
      author="Pierre Calvet",
      author_email="support@babbar.tech",
      license="MIT",
      packages=find_packages(),      
	  install_requires=[
          "requests",
           "pandas"]
)

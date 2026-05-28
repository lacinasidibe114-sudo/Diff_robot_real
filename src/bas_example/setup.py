from setuptools import find_packages, setup

package_name = 'bas_example'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sidibe',
    maintainer_email='sidibe@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'simple_publisher = bas_example.simple_publisher:main',
            'simple_subscriber = bas_example.simple_subscriber:main',
            'simple_parameter = bas_example.simple_parameter:main',
            'simple_tf_kinematics = bas_example.simple_tf_kinematics:main', 
            'simple_service_server = bas_example.simple_service_server:main',
            'simple_service_client = bas_example.simple_service_client:main',
            'simple_tf_kinematics_request = bas_example.simple_tf_kinematics_request:main',
            'simple_lifecycle_node = bas_example.simple_lifecycle_node:main'


            
        ],
    },
)

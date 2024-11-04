import numpy as np
import cv2
import os
import time


class RoboticArm:
    def __init__(self):
        self.position = {"x": 0, "y": 0, "z": 0}

    def move_to(self, x, y, z):
        """Move the robotic arm to the specified position."""
        self.position = {"x": x, "y": y, "z": z}
        print(f"Robotic arm moved to position: {self.position}")

    def get_position(self):
        return self.position

    def adjust_for_tremor(self, dx, dy, dz):
        """Simulates tremor reduction by adjusting small, unwanted movements."""
        self.position["x"] += dx * 0.1
        self.position["y"] += dy * 0.1
        self.position["z"] += dz * 0.1
        print(f"Tremor reduced position: {self.position}")


class SurgicalCamera:
    def __init__(self):
        self.camera_position = {"x": 0, "y": 0, "z": 0}

    def capture_image(self, image_path):
        """Capture the provided image from the specified path."""
        if os.path.exists(image_path):
            img = cv2.imread(image_path)
            print("Image captured by surgical camera.")
            return img
        else:
            print("Image file not found.")
            return None

    def display_image(self, image):
        """Displays the processed image."""
        cv2.imshow("Surgical Camera View", image)
        cv2.waitKey(1)


class SurgeonConsole:
    def __init__(self):
        self.arm = RoboticArm()
        self.camera = SurgicalCamera()

    def direct_arm(self, x, y, z):
        """Directs the robotic arm to a specific position."""
        print(f"Surgeon directs arm to position ({x}, {y}, {z}).")
        self.arm.move_to(x, y, z)

    def reduce_tremor(self, dx, dy, dz):
        """Simulate tremor reduction by adjusting the robotic arm position."""
        self.arm.adjust_for_tremor(dx, dy, dz)

    def capture_and_process_image(self, image_path):
        """Captures and processes an image for display and analysis."""
        image = self.camera.capture_image(image_path)
        if image is not None:
            self.camera.display_image(image)
            return image
        return None


def detect_tumor(image):
    """Basic tumor detection using image processing techniques."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    tumor_contour = max(contours, key=cv2.contourArea) if contours else None
    if tumor_contour is not None:
        cv2.drawContours(image, [tumor_contour], -1, (255, 0, 255), 2)
        print("Tumor detected and highlighted.")
        return tumor_contour
    else:
        print("No tumor detected.")
        return None


def draw_arrows_and_square(image, tumor_contour, arm_position):
    """Draws a square around the tumor and arrows pointing to it."""
    x, y, w, h = cv2.boundingRect(tumor_contour)

    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    arm_x, arm_y = arm_position["x"], arm_position["y"]
    left_arrow_start = (arm_x, arm_y)
    left_arrow_end = (x, y + h // 2)
    cv2.arrowedLine(image, left_arrow_start, left_arrow_end,
                    (0, 255, 255), 2, tipLength=0.1)

    right_arrow_start = (arm_x + 100, arm_y)
    right_arrow_end = (x + w, y + h // 2)
    cv2.arrowedLine(image, right_arrow_start, right_arrow_end,
                    (0, 255, 255), 2, tipLength=0.1)

    return (x, y, w, h)


def remove_tumor(image, tumor_contour):
    """Simulates tumor removal by drawing a gray circle on the tumor region."""
    print("Removing the tumor is in process...")

    M = cv2.moments(tumor_contour)
    if M['m00'] != 0:
        cX = int(M['m10'] / M['m00'])
        cY = int(M['m01'] / M['m00'])

        cv2.circle(image, (cX, cY), 20, (128, 128, 128), -1)

    time.sleep(2)
    print("Tumor removed successfully.")

    return image


def create_combined_image(before_image, after_image):
    """Combine two images side by side with labels."""
    combined_image = np.hstack((before_image, after_image))

    cv2.putText(combined_image, "Before", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(combined_image, "After",
                (before_image.shape[1] + 20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return combined_image


def simulate_surgery(image_path):
    console = SurgeonConsole()

    image = console.capture_and_process_image(image_path)
    if image is None:
        return

    tumor_contour = detect_tumor(image)
    if tumor_contour is not None:

        M = cv2.moments(tumor_contour)
        tumor_center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        arm_position = {"x": 50, "y": 150}

        before_image = image.copy()
        draw_arrows_and_square(image, tumor_contour, arm_position)

        console.camera.display_image(image)

        print("Preparing to remove the tumor...")
        time.sleep(2)

        console.direct_arm(tumor_center[0], tumor_center[1], -2)
        console.reduce_tremor(0.1, 0.1, 0.1)

        after_image = remove_tumor(image.copy(), tumor_contour)

        x, y, w, h = cv2.boundingRect(tumor_contour)
        cv2.rectangle(after_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.drawContours(after_image, [tumor_contour], -1, (0, 255, 0), 2)

        combined_image = create_combined_image(before_image, after_image)

        output_path = "surgery_result.jpg"
        cv2.imwrite(output_path, combined_image)

        print(f"Combined image saved as '{output_path}'.")

        console.camera.display_image(combined_image)

        print("Press any key to exit...")
        while True:
            if cv2.waitKey(1) != -1:
                break

        cv2.destroyAllWindows()
        print("Exiting the program.")


if __name__ == "__main__":

    image_path = "MRI-Brain-Images-abenign-bmalignant-images.jpg"
    simulate_surgery(image_path)

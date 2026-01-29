import os
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from android.permissions import request_permissions, Permission
from jnius import autoclass, cast

# Android API Classes
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')

class WhatsAppSlideshow(App):
    def build(self):
        self.image_list = []
        self.temp_folder = os.path.join(self.user_data_dir, "temp_frames")
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        # UI Layout
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        self.label = Label(
            text="Step 1: Select images in WhatsApp\nStep 2: Share to this App\nStep 3: Click Build Video",
            halign="center", font_size='18sp'
        )
        self.layout.add_widget(self.label)
        
        self.build_btn = Button(
            text="BUILD VIDEO", 
            size_hint=(1, 0.3),
            background_color=(0, 0.7, 0, 1)
        )
        self.build_btn.bind(on_release=self.generate_slideshow)
        self.layout.add_widget(self.build_btn)

        # Request Permissions for Android 10+
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE, 
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        # Check for shared content after app loads
        Clock.schedule_once(lambda dt: self.handle_whatsapp_share(), 1)
        
        return self.layout

    def handle_whatsapp_share(self):
        activity = PythonActivity.mActivity
        intent = activity.getIntent()
        action = intent.getAction()
        mimetype = intent.getType()

        if action in [Intent.ACTION_SEND, Intent.ACTION_SEND_MULTIPLE] and mimetype:
            # Catch the caption (text)
            caption = intent.getStringExtra(Intent.EXTRA_TEXT) or ""
            
            if action == Intent.ACTION_SEND:
                uri = intent.getParcelableExtra(Intent.EXTRA_STREAM)
                self.save_uri_to_file(uri, caption)
            else:
                uris = intent.getParcelableArrayListExtra(Intent.EXTRA_STREAM)
                for i in range(uris.size()):
                    self.save_uri_to_file(uris.get(i), caption)
            
            self.label.text = f"Ready! Received {len(self.image_list)} images."

    def save_uri_to_file(self, uri, caption):
        """Processes the Android URI, adds caption, and saves locally."""
        try:
            # Note: On Android, we must open a stream to read the shared URI
            context = PythonActivity.mActivity.getApplicationContext()
            content_resolver = context.getContentResolver()
            stream = content_resolver.openInputStream(uri)
            
            # Convert stream to numpy array for OpenCV
            data = stream.readAllBytes()
            nparr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is not None:
                # Add caption to image if it exists
                if caption:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img, caption, (50, img.shape[0]-50), font, 1.5, (255,255,255), 3)

                filename = os.path.join(self.temp_folder, f"img_{len(self.image_list):03d}.png")
                cv2.imwrite(filename, img)
                self.image_list.append(filename)
        except Exception as e:
            self.label.text = f"Error processing image: {str(e)}"

    def generate_slideshow(self, instance):
        if not self.image_list:
            self.label.text = "No images shared yet!"
            return

        self.label.text = "Creating Video... Please wait."
        
        # Slideshow logic
        output_path = "/sdcard/Download/whatsapp_slideshow.avi"
        img = cv2.imread(self.image_list[0])
        h, w, _ = img.shape
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video = cv2.VideoWriter(output_path, fourcc, 0.5, (w, h))

        for img_path in self.image_list:
            frame = cv2.imread(img_path)
            # Resize to match first image
            frame = cv2.resize(frame, (w, h))
            video.write(frame)

        video.release()
        self.label.text = f"SUCCESS!\nVideo saved in Downloads folder."

if __name__ == '__main__':
    WhatsAppSlideshow().run()